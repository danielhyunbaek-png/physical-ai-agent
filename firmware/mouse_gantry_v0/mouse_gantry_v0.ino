// mouse_gantry_v0.ino
// Wave 2 mouse rig firmware: Cartesian XY gantry carrying a Logitech B100
// (or an animatronic hand riding it), SG90 servos for L/R click.
//
// STATUS: written AHEAD of the Wave 2 hardware decision (gantry favored for
// TFT's drag requirement). The serial protocol below is the contract with
// agent/mouse_driver.py GantryMouse -- if Wave 2 lands on a pantograph or
// another mechanism, keep the protocol and rewrite the motion code only;
// the Python side (and the whole agent) won't notice.
//
// HARDWARE ASSUMPTION (adjust the #defines, nothing else):
//   Arduino Uno/Nano + 2x A4988/DRV8825 on CNC-shield-style pins:
//     X: STEP=2 DIR=5   Y: STEP=3 DIR=6   ENABLE=8 (active LOW, shared)
//     Endstops: X_MIN=9, Y_MIN=10 (NO switches to GND, INPUT_PULLUP)
//     Servos: LEFT=11, RIGHT=12
//   GT2 belt + 20T pulley at 1/8 microstep = 80 steps/mm (the default).
//   No endstops yet? set HAVE_ENDSTOPS 0 -- HOME then just zeros in place
//   (park the carriage at the corner by hand first).
//
// Serial protocol (115200 baud, newline; every command answers OK or ERR):
//   HOME                  seek endstops (or zero in place), position = (0,0)
//   MOVE <x_mm> <y_mm>    absolute move, soft-limited to the pad
//   JOG <dx_mm> <dy_mm>   relative move
//   BTN <L|R> <DOWN|UP>   press / release a click servo (drag support)
//   CLICK <L|R> [ms]      press, hold (default 80ms), release -- atomic
//   SPEED <mm_s>          set cruise speed (default 120, max 250)
//   STATUS                position, speed, button states
//   STOP                  release both buttons, disable motors
//
// SAFETY: same power-on rule family as keyboard_v1 -- USB first, THEN motor
// 12V. Motors are disabled (EN high) until the first motion command.

#include <Servo.h>

// ---- pins (CNC shield convention) ------------------------------------------
const uint8_t PIN_XSTEP = 2, PIN_XDIR = 5;
const uint8_t PIN_YSTEP = 3, PIN_YDIR = 6;
const uint8_t PIN_EN    = 8;                  // active LOW, both drivers
const uint8_t PIN_XMIN  = 9, PIN_YMIN = 10;   // NO -> GND, INPUT_PULLUP
const uint8_t PIN_SRVL  = 11, PIN_SRVR = 12;

// ---- geometry / motion (EDIT to match the build) -----------------------------
#define HAVE_ENDSTOPS   0        // 0 until endstops are wired
const float STEPS_PER_MM = 80.0; // GT2 20T @ 1/8 microstep
const float PAD_W_MM     = 300.0;
const float PAD_H_MM     = 200.0;
const float HOME_BACKOFF = 3.0;  // mm off the switch after homing
float  cruise_mm_s       = 120.0;
const float MAX_MM_S     = 250.0;
const float MIN_MM_S     = 10.0;
const float ACCEL_MM_S2  = 400.0;
// X DIR polarity: 1 if HIGH moves +X (away from the X switch), else 0
#define XDIR_POS 1
#define YDIR_POS 1

// ---- click servos -------------------------------------------------------------
const uint8_t SERVO_REST_L  = 20,  SERVO_PRESS_L = 55;   // tune on the rig
const uint8_t SERVO_REST_R  = 20,  SERVO_PRESS_R = 55;
const uint16_t CLICK_MS_DEFAULT = 80;

Servo servoL, servoR;
bool btnL = false, btnR = false;
float posX = 0, posY = 0;        // believed position, mm
bool motorsOn = false;
char lineBuf[64];
uint8_t lineLen = 0;

// ---- low-level motion ------------------------------------------------------------
void motors(bool on) {
  digitalWrite(PIN_EN, on ? LOW : HIGH);
  if (on && !motorsOn) delay(5);             // driver wake
  motorsOn = on;
}

// Ramped Bresenham line: both axes finish together; trapezoid speed profile.
void moveSteps(long sx, long sy) {
  if (sx == 0 && sy == 0) return;
  motors(true);
  digitalWrite(PIN_XDIR, (sx >= 0) == XDIR_POS ? HIGH : LOW);
  digitalWrite(PIN_YDIR, (sy >= 0) == YDIR_POS ? HIGH : LOW);
  long ax = labs(sx), ay = labs(sy);
  long major = max(ax, ay), minor = min(ax, ay);
  uint8_t pinMaj = (ax >= ay) ? PIN_XSTEP : PIN_YSTEP;
  uint8_t pinMin = (ax >= ay) ? PIN_YSTEP : PIN_XSTEP;

  // speed profile in major-axis steps
  float v = MIN_MM_S, vmax = cruise_mm_s;
  long rampSteps = (long)((vmax * vmax - v * v) /
                          (2 * ACCEL_MM_S2) * STEPS_PER_MM);
  rampSteps = max(1L, min(rampSteps, major / 2));
  long err = major / 2;
  for (long i = 0; i < major; i++) {
    // trapezoid: accelerate, cruise, decelerate
    float frac;
    if (i < rampSteps)              frac = (float)(i + 1) / rampSteps;
    else if (i >= major - rampSteps) frac = (float)(major - i) / rampSteps;
    else                            frac = 1.0;
    float mmps = MIN_MM_S + (vmax - MIN_MM_S) * frac;
    unsigned int usHalf = (unsigned int)(1e6 / (mmps * STEPS_PER_MM) / 2);

    digitalWrite(pinMaj, HIGH);
    err -= minor;
    bool stepMin = false;
    if (err < 0) { err += major; stepMin = true; }
    if (stepMin) digitalWrite(pinMin, HIGH);
    delayMicroseconds(max(usHalf, 3u));
    digitalWrite(pinMaj, LOW);
    if (stepMin) digitalWrite(pinMin, LOW);
    delayMicroseconds(max(usHalf, 3u));
  }
}

void moveToMM(float x, float y) {
  x = constrain(x, 0.0f, PAD_W_MM);
  y = constrain(y, 0.0f, PAD_H_MM);
  long sx = lround((x - posX) * STEPS_PER_MM);
  long sy = lround((y - posY) * STEPS_PER_MM);
  moveSteps(sx, sy);
  posX += sx / STEPS_PER_MM;      // track what we actually stepped
  posY += sy / STEPS_PER_MM;
}

void homeAxes() {
#if HAVE_ENDSTOPS
  motors(true);
  // seek -X then -Y at slow speed until switches close
  digitalWrite(PIN_XDIR, XDIR_POS ? LOW : HIGH);
  while (digitalRead(PIN_XMIN) == HIGH) {
    digitalWrite(PIN_XSTEP, HIGH); delayMicroseconds(400);
    digitalWrite(PIN_XSTEP, LOW);  delayMicroseconds(400);
  }
  digitalWrite(PIN_YDIR, YDIR_POS ? LOW : HIGH);
  while (digitalRead(PIN_YMIN) == HIGH) {
    digitalWrite(PIN_YSTEP, HIGH); delayMicroseconds(400);
    digitalWrite(PIN_YSTEP, LOW);  delayMicroseconds(400);
  }
  posX = posY = 0;
  moveToMM(HOME_BACKOFF, HOME_BACKOFF);
  posX = posY = 0;                 // backoff point is the working origin
#else
  posX = posY = 0;                 // trust the hand-parked corner
#endif
}

// ---- buttons -----------------------------------------------------------------------
void setButton(char which, bool down) {
  if (which == 'L') {
    servoL.write(down ? SERVO_PRESS_L : SERVO_REST_L);
    btnL = down;
  } else {
    servoR.write(down ? SERVO_PRESS_R : SERVO_REST_R);
    btnR = down;
  }
}

// ---- command handling ---------------------------------------------------------------
void handle(char *line) {
  char *cmd = strtok(line, " ");
  if (!cmd) return;

  if (!strcasecmp(cmd, "HOME")) {
    homeAxes();
    Serial.println(F("OK HOME"));

  } else if (!strcasecmp(cmd, "MOVE") || !strcasecmp(cmd, "JOG")) {
    bool rel = !strcasecmp(cmd, "JOG");
    char *sx = strtok(NULL, " "), *sy = strtok(NULL, " ");
    if (!sx || !sy) { Serial.println(F("ERR MOVE <x> <y>")); return; }
    float x = atof(sx), y = atof(sy);
    if (rel) { x += posX; y += posY; }
    moveToMM(x, y);
    Serial.print(F("OK POS ")); Serial.print(posX, 2);
    Serial.print(' '); Serial.println(posY, 2);

  } else if (!strcasecmp(cmd, "BTN")) {
    char *w = strtok(NULL, " "), *st = strtok(NULL, " ");
    if (!w || !st || (toupper(w[0]) != 'L' && toupper(w[0]) != 'R')) {
      Serial.println(F("ERR BTN <L|R> <DOWN|UP>")); return;
    }
    setButton(toupper(w[0]), !strcasecmp(st, "DOWN"));
    Serial.println(F("OK BTN"));

  } else if (!strcasecmp(cmd, "CLICK")) {
    char *w = strtok(NULL, " "), *ms = strtok(NULL, " ");
    char which = w ? toupper(w[0]) : 'L';
    if (which != 'L' && which != 'R') {
      Serial.println(F("ERR CLICK <L|R> [ms]")); return;
    }
    uint16_t hold = ms ? constrain(atoi(ms), 20, 1000) : CLICK_MS_DEFAULT;
    setButton(which, true);  delay(hold);
    setButton(which, false); delay(30);
    Serial.println(F("OK CLICK"));

  } else if (!strcasecmp(cmd, "SPEED")) {
    char *v = strtok(NULL, " ");
    if (v) cruise_mm_s = constrain(atof(v), MIN_MM_S, MAX_MM_S);
    Serial.print(F("OK SPEED ")); Serial.println(cruise_mm_s, 1);

  } else if (!strcasecmp(cmd, "STATUS")) {
    Serial.print(F("OK POS ")); Serial.print(posX, 2);
    Serial.print(' ');          Serial.print(posY, 2);
    Serial.print(F(" SPEED ")); Serial.print(cruise_mm_s, 1);
    Serial.print(F(" L"));      Serial.print(btnL ? F("DOWN") : F("UP"));
    Serial.print(F(" R"));      Serial.println(btnR ? F("DOWN") : F("UP"));

  } else if (!strcasecmp(cmd, "STOP")) {
    setButton('L', false); setButton('R', false);
    motors(false);
    Serial.println(F("OK STOP"));

  } else {
    Serial.print(F("ERR unknown: ")); Serial.println(cmd);
  }
}

void setup() {
  pinMode(PIN_XSTEP, OUTPUT); pinMode(PIN_XDIR, OUTPUT);
  pinMode(PIN_YSTEP, OUTPUT); pinMode(PIN_YDIR, OUTPUT);
  pinMode(PIN_EN, OUTPUT);    digitalWrite(PIN_EN, HIGH);   // disabled
  pinMode(PIN_XMIN, INPUT_PULLUP); pinMode(PIN_YMIN, INPUT_PULLUP);
  servoL.attach(PIN_SRVL); servoR.attach(PIN_SRVR);
  setButton('L', false); setButton('R', false);
  Serial.begin(115200);
  Serial.println(F("mouse_gantry_v0 ready (HOME first)"));
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (lineLen) { lineBuf[lineLen] = 0; handle(lineBuf); lineLen = 0; }
    } else if (lineLen < sizeof(lineBuf) - 1) {
      lineBuf[lineLen++] = c;
    }
  }
}
