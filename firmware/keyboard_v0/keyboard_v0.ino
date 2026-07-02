// keyboard_v0.ino
// Week 2 acceptance firmware  (rev: Option-1 low-power pulses + TYPE/MAP)
// Drives up to 8 solenoid channels via one 74HC595 + one ULN2803A.
//
// POWER NOTE (Option 1):
//   Heat/energy per keystroke scales ~linearly with on-time. Keep the pulse as
//   short as still registers (tune live with PULSE), then stop there.
//   Default is 22 ms -- the value found good on the 2x2 prototype.
//
// TYPING:
//   keymap[] below says which letter each channel presses. Once it matches your
//   FIRE 0..3 test, "TYPE freed" presses the right keys to spell the word.
//   Any letter with no solenoid under it prints '?' and is skipped.
//
// Serial commands:
//   FIRE  <ch> [ms]                  fire one channel (ch = 0..7)
//     FIRE 0            -> default pulse;   FIRE 0 40 -> explicit 40 ms
//   PULSE [ms]                       set/get the default pulse length
//   BURST [<n> [<pulse> [<gap>]]]    fire channels 0..n-1 in sequence
//   TYPE  <text>                     press keys to spell text (waits LEAD ms first)
//     TYPE freed
//   LEAD  [ms]                       set/get the head-start delay before TYPE (default 1500)
//     LEAD 2000         -> wait 2 s so you can click your target window
//   MAP   [<ch> <letter>]            set/show the channel->key map
//     MAP 0 f           -> channel 0 presses 'f';   MAP -> show whole map
//   ALLOFF                           force every channel low
//
// Wiring summary
//   74HC595 -> Arduino Mega: DS=D11, SH_CP=D12, ST_CP=D13, OE=GND, MR=+5V.
//   74HC595 Q0..Q7 -> ULN2803A inputs IN1..IN8 (1:1).
//   ULN2803A outputs OUT1..OUT8 -> low side of each solenoid coil.
//   Solenoid high side -> +12V from PSU.
//   ULN2803A COM (pin 10) -> +12V    <-- enables internal flyback diodes.
//   ULN2803A GND (pin  9) -> PSU GND AND Arduino GND (common ground).
//   Bulk cap: 470 uF (or larger) across the 12V solenoid rail close to ULN.
//
// Safety
//   - Never connect the 12V rail to the Arduino 5V. Only the grounds tie.
//   - Keep pulses short to limit heat. If a coil stays hot, shorten the pulse.

const uint8_t PIN_DATA  = 11;  // 595 DS
const uint8_t PIN_CLOCK = 12;  // 595 SH_CP
const uint8_t PIN_LATCH = 13;  // 595 ST_CP

const uint8_t NUM_CHANNELS = 8;        // one SR for now

// ---- TUNABLE TIMING (Option 1: shorter pulse = less heat/power) -------------
uint16_t       defaultPulseMs = 40;    // working pulse, runtime-settable via PULSE
const uint16_t MAX_PULSE_MS   = 200;   // hard safety ceiling
const uint16_t MIN_GAP_MS     = 20;    // enforced cooldown between fires
const uint16_t BURST_GAP_MS   = 100;   // default gap between channels in BURST
uint16_t       typeLeadMs     = 1500;  // TYPE waits this long before pressing (time to click target)
// -----------------------------------------------------------------------------

// ---- CHANNEL -> KEY MAP -----------------------------------------------------
// keymap[channel] = the lowercase letter that channel's solenoid presses.
// VERIFY with FIRE 0..3 and fix any that are wrong (edit here, or MAP at runtime).
// 0 = unused channel. Set from your test: ch0=e ch1=r ch2=d ch3=f (spells "freed").
char keymap[NUM_CHANNELS] = { 'e', 'r', 'd', 'f', 0, 0, 0, 0 };
// -----------------------------------------------------------------------------

uint8_t  shadow = 0x00;                // mirrors the 595 output state
uint32_t lastFireEndMs = 0;

void writeShadow() {
  digitalWrite(PIN_LATCH, LOW);
  shiftOut(PIN_DATA, PIN_CLOCK, MSBFIRST, shadow);
  digitalWrite(PIN_LATCH, HIGH);
}

void setChannel(uint8_t ch, bool on) {
  if (ch >= NUM_CHANNELS) return;
  if (on) shadow |=  (1 << ch);
  else    shadow &= ~(1 << ch);
  writeShadow();
}

// quiet actuation shared by FIRE and TYPE (no serial chatter)
void firePulse(uint8_t ch, uint16_t ms) {
  if (ch >= NUM_CHANNELS) return;
  if (ms == 0)           ms = defaultPulseMs;
  if (ms > MAX_PULSE_MS) ms = MAX_PULSE_MS;

  uint32_t now = millis();
  if (now - lastFireEndMs < MIN_GAP_MS) {
    delay(MIN_GAP_MS - (now - lastFireEndMs));
  }
  setChannel(ch, true);
  delay(ms);
  setChannel(ch, false);
  lastFireEndMs = millis();
}

void fire(uint8_t ch, uint16_t ms) {
  if (ch >= NUM_CHANNELS) {
    Serial.print(F("ERR bad channel ")); Serial.println(ch);
    return;
  }
  if (ms == 0)           ms = defaultPulseMs;
  if (ms > MAX_PULSE_MS) ms = MAX_PULSE_MS;
  firePulse(ch, ms);
  Serial.print(F("OK FIRE ")); Serial.print(ch);
  Serial.print(' '); Serial.println(ms);
}

void burst(int count, int pulse, int gap) {
  if (count < 1) count = 1;
  if (count > NUM_CHANNELS) count = NUM_CHANNELS;
  if (pulse < 1) pulse = 1;
  if (pulse > MAX_PULSE_MS) pulse = MAX_PULSE_MS;
  if (gap < (int)MIN_GAP_MS) gap = MIN_GAP_MS;

  Serial.print(F("OK BURST ")); Serial.print(count);
  Serial.print(' '); Serial.print(pulse);
  Serial.print(' '); Serial.println(gap);

  for (uint8_t ch = 0; ch < count; ch++) {
    setChannel(ch, true);
    delay(pulse);
    setChannel(ch, false);
    if (ch < count - 1) delay(gap);
  }
  lastFireEndMs = millis();
}

// find which channel presses letter c (case-insensitive); -1 if none
int channelForKey(char c) {
  if (c >= 'A' && c <= 'Z') c += 32;           // to lowercase
  for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++) {
    char k = keymap[ch];
    if (k >= 'A' && k <= 'Z') k += 32;
    if (k && k == c) return ch;
  }
  return -1;
}

// press the keys to spell s, one letter at a time
void typeText(const char *s) {
  if (typeLeadMs) {
    Serial.print(F("TYPE in ")); Serial.print(typeLeadMs);
    Serial.println(F(" ms -- click your target window now..."));
    delay(typeLeadMs);
  }
  Serial.print(F("OK TYPE "));
  for (const char *p = s; *p; p++) {
    char c = *p;
    if (c == ' ') { Serial.print(' '); delay(60); continue; }  // no space key here
    int ch = channelForKey(c);
    if (ch < 0) { Serial.print('?'); continue; }               // no solenoid for it
    firePulse((uint8_t)ch, defaultPulseMs);
    delay(60);                 // settle + clean release so doubled letters register
    Serial.print(c);
  }
  Serial.println();
}

void printMap() {
  Serial.print(F("MAP"));
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
    Serial.print(' '); Serial.print((int)i); Serial.print(':');
    if (keymap[i]) Serial.print(keymap[i]); else Serial.print('-');
  }
  Serial.println();
}

// ---- tiny line-based serial parser ----
char  buf[48];
uint8_t bufLen = 0;

void handleLine(char *line) {
  if (strncmp(line, "FIRE", 4) == 0) {
    int ch = -1, ms = -1;
    int n = sscanf(line + 4, "%d %d", &ch, &ms);
    if (n >= 1 && ch >= 0) {
      if (n < 2 || ms < 0) ms = defaultPulseMs;   // FIRE <ch> -> default pulse
      fire((uint8_t)ch, (uint16_t)ms);
    } else {
      Serial.println(F("ERR usage: FIRE <ch> [ms]"));
    }
  } else if (strncmp(line, "PULSE", 5) == 0) {
    int ms = -1;
    if (sscanf(line + 5, "%d", &ms) == 1 && ms > 0) {
      if (ms > MAX_PULSE_MS) ms = MAX_PULSE_MS;
      defaultPulseMs = (uint16_t)ms;
      Serial.print(F("OK PULSE ")); Serial.println(defaultPulseMs);
    } else {
      Serial.print(F("PULSE ")); Serial.println(defaultPulseMs);  // report only
    }
  } else if (strncmp(line, "BURST", 5) == 0) {
    int count = 4, pulse = defaultPulseMs, gap = BURST_GAP_MS;
    sscanf(line + 5, "%d %d %d", &count, &pulse, &gap);
    burst(count, pulse, gap);
  } else if (strncmp(line, "TYPE", 4) == 0) {
    const char *txt = line + 4;
    while (*txt == ' ') txt++;                     // skip leading spaces
    if (*txt == 0) Serial.println(F("ERR usage: TYPE <text>"));
    else typeText(txt);
  } else if (strncmp(line, "LEAD", 4) == 0) {
    int ms = -1;
    if (sscanf(line + 4, "%d", &ms) == 1 && ms >= 0) {
      if (ms > 10000) ms = 10000;                  // cap at 10 s
      typeLeadMs = (uint16_t)ms;
      Serial.print(F("OK LEAD ")); Serial.println(typeLeadMs);
    } else {
      Serial.print(F("LEAD ")); Serial.println(typeLeadMs);   // report only
    }
  } else if (strncmp(line, "MAP", 3) == 0) {
    int ch = -1; char c = 0;
    if (sscanf(line + 3, "%d %c", &ch, &c) == 2 && ch >= 0 && ch < NUM_CHANNELS) {
      keymap[ch] = c;
      Serial.print(F("OK MAP ")); Serial.print(ch);
      Serial.print(' '); Serial.println(c);
    } else {
      printMap();                                  // no/invalid args -> show map
    }
  } else if (strcmp(line, "ALLOFF") == 0) {
    shadow = 0x00;
    writeShadow();
    Serial.println(F("OK ALLOFF"));
  } else if (line[0] != 0) {
    Serial.print(F("ERR unknown: ")); Serial.println(line);
  }
}

void setup() {
  pinMode(PIN_DATA, OUTPUT);
  pinMode(PIN_CLOCK, OUTPUT);
  pinMode(PIN_LATCH, OUTPUT);
  shadow = 0x00;
  writeShadow();              // make sure every channel is OFF at boot
  Serial.begin(115200);
  Serial.print(F("keyboard_v0 ready (pulse "));
  Serial.print(defaultPulseMs);
  Serial.println(F(" ms). cmds: FIRE <ch>[ms] | PULSE [ms] | BURST [n p g] | TYPE <text> | LEAD [ms] | MAP [ch c] | ALLOFF"));
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\r') continue;
    if (c == '\n' || bufLen >= sizeof(buf) - 1) {
      buf[bufLen] = 0;
      handleLine(buf);
      bufLen = 0;
    } else {
      buf[bufLen++] = c;
    }
  }
}
