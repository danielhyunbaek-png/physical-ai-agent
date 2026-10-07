// keyboard_v1.ino
// Full 84-key production firmware for the Physical AI Agent.
// Drives 88 solenoid channels via 11x 74HC595 (cascaded) -> 11x ULN2803A.
//
// LINEAGE: scales keyboard_v0 (1 cell / 8 ch) to 11 cells / 88 ch and adds:
//   - named keys (Enter, Bksp, LShift, arrows, F-keys...) from the Air75 layout
//   - TYPE with shift chords: uppercase + shifted symbols press LShift for real
//   - KEY / CHORD / HOLD / RELEASE for modifier combos (e.g. CHORD LCmd+Space)
//   - WALK mode: fire channels in sequence to verify the solder-time MAP log
//   - EEPROM-persisted keymap (SAVE/LOAD) -- edit MAP at runtime, no recompile
//   - per-channel refire cooldown + max-simultaneous-ON guard (PSU/thermal)
//
// CHANNEL NUMBERING (canonical wiring, as-built July 1 2026, all 11 cells):
//   Q0->IN1 ... Q7->IN8, so channel N -> cell (N/8 + 1), ULN OUT(N%8 + 1).
//   FIRE 0  = cell #1 OUT1.  FIRE 87 = cell #11 OUT8.  Channels are sequential;
//   only the channel->KEY map (which key each OUT wire lands on) is data.
//   Cells 1-4 = Board A, 5-8 = Board B, 9-11 = Board C (3-board split).
//
// CASCADE ASSUMPTION: cell #1's 595 is the chip wired to the Mega (DS=D11);
//   each Q7' feeds the next cell's DS. writeShadow() therefore shifts cell 11's
//   byte FIRST and cell 1's byte LAST. If WALK lights cells in reverse order,
//   flip CASCADE_REVERSED to 1 -- do not rewire.
//
// POWER-ON SAFETY (read before first flash on the full plate):
//   A 595 outputs RANDOM data from power-up until setup() clears it. On 84
//   solenoids that's potential random 12V pulses at every boot.
//   FIXED IN HARDWARE on the driver PCB (Jul 2026): R1 (10k) pulls ~OE HIGH
//   = outputs disabled, and ~OE is routed to J71 pin 6 -> Mega D10 (PIN_OE).
//   setup() holds OE HIGH, clears all registers, and only then drives it LOW.
//   CONSEQUENCE: D10 must actually be wired. If ~OE is left floating on the
//   pullup, every channel is disabled and NOTHING FIRES -- serial still
//   responds and WALK still prints, so the symptom looks like dead solenoids.
//   Keep the operating rule anyway: BRING UP THE ARDUINO (USB) FIRST, THEN
//   switch on the 12V rail.
//
// Serial commands (115200 baud, Newline):
//   FIRE <ch> [ms]          fire one channel (0..87)
//   PULSE [ms]              set/get default pulse (22ms = 2x2-validated value)
//   WALK [s [e [ms [gap]]]] fire channels s..e in sequence (default 0..87).
//                           Prints each channel; any serial input aborts.
//                           THE MAP-verification pass: watch which key clicks.
//   TYPE <text>             type text; handles uppercase + shifted symbols
//   KEY <name>              press one named key (KEY Enter, KEY F5, KEY Up)
//   CHORD <a>+<b>[+<c>...]  hold all but last, fire last, release (reverse order)
//   HOLD <name|ch>          hold a channel ON (auto-releases after 10 s)
//   RELEASE <name|ch|ALL>   release held channel(s)
//   MAP [<ch> <key|->]      set/clear/show channel->key map (MAP 12 Enter)
//   SAVE / LOAD             persist / restore keymap to EEPROM
//   LEAD [ms]               head-start delay before TYPE (default 1500)
//   REPEAT <ch> <p> <per> <n> speed test: fire one coil n times every per ms
//
//   FAST-TYPE / STREAM (Oct 3 2026, brief 09 -- the 320 WPM Monkeytype path):
//   Non-blocking, schedule-based. A new key-down every 12000/WPM ms; each coil
//   ON for FPULSE ms; pulses of DIFFERENT keys overlap; the SAME key waits
//   SAMEKEY ms start-to-start (measured Oct 3: 45 ms). Lowercase + space only
//   (no shift in stream). Unmapped chars keep their time slot but fire nothing
//   (so one mapped coil can be tested: FAST jajaja).
//   Q <text>                append text VERBATIM to the stream queue (1024 B);
//                           replies "K <free bytes>" (host waits for K = flow ctl)
//   GO                      start typing the queue after LEAD ms
//   END                     no more text coming: finish when the queue drains
//   FAST <text>             = clear + Q <text> + END + GO  (Serial Monitor test)
//   STOP                    abort now: queue cleared, all coils off, stats
//   WPM [n]                 schedule speed (default 330 = 36.4 ms/char)
//   FPULSE [ms]             stream pulse (default 20, measured Oct 3)
//   SAMEKEY [ms]            same-coil start-to-start minimum (default 45)
//   While a stream runs only Q/END/STOP/ALLOFF/STATUS/WPM/FPULSE/SAMEKEY are
//   accepted (everything else blocks and would wreck the timing -> ERR busy).
//   Finish prints:  DONE slots=.. fired=.. skipped=.. shift=.. same=..
//                   under=.. lateMax=..us ms=.. wpm=..
//   STATUS                  pulse, lead, mapped count, held channels, fire count
//   ALLOFF                  force every channel low
//
// Wiring per cell is unchanged from keyboard_v0 / OneCell guide:
//   595: DS<-prev(or D11), SH_CP=D12 (bused), ST_CP=D13 (bused), MR=+5V,
//        OE=~OE bus -> R1 10k pullup to +5V -> J71 pin 6 -> Mega D10
//        (breadboard rig instead straps OE to GND; then set PIN_OE = 255)
//   ULN: IN1-8 <- Q0-7 canonical, COM(10) -> +12V (flyback -- never skip),
//        GND(9) -> star ground. 0.1uF per chip, bulk cap on the 12V rail.

#include <EEPROM.h>

// ---- pins -------------------------------------------------------------------
const uint8_t PIN_DATA  = 11;   // 595 DS (cell #1)
const uint8_t PIN_CLOCK = 12;   // 595 SH_CP (bused to all cells)
const uint8_t PIN_LATCH = 13;   // 595 ST_CP (bused to all cells)
const uint8_t PIN_OE    = 10;   // 595 OE (active LOW), driver PCB J71 pin 6.
                                // The PCB carries R1, a 10k pullup holding ~OE
                                // HIGH (= outputs DISABLED) at power-up. This pin
                                // MUST be driven or nothing ever fires: setup()
                                // holds it HIGH, clears the registers, then drops
                                // it LOW. Set back to 255 only for the breadboard
                                // rig, where OE is strapped to GND.
#define CASCADE_REVERSED 0      // set 1 if WALK proves cell order is flipped

// ---- geometry ----------------------------------------------------------------
const uint8_t NUM_CELLS    = 11;
const uint8_t NUM_CHANNELS = NUM_CELLS * 8;   // 88 (84 keys + 4 spare)

// ---- tunable timing -----------------------------------------------------------
uint16_t       defaultPulseMs = 22;    // 2x2-validated; retune at scale w/ PULSE
const uint16_t MAX_PULSE_MS   = 200;   // hard ceiling
const uint16_t MIN_GAP_MS     = 15;    // global gap between any two fires
const uint16_t REFIRE_MS      = 60;    // per-channel cooldown (doubled letters)
const uint16_t SETTLE_MS      = 60;    // inter-key settle inside TYPE
const uint16_t CHORD_SEAT_MS  = 30;    // modifier seat time before the keypress
const uint32_t MAX_HOLD_MS    = 10000; // auto-release safety for HOLD
uint16_t       typeLeadMs     = 1500;
const uint8_t  MAX_ON         = 7;     // PSU budget: 7 x 300mA + transients

// ---- key table -----------------------------------------------------------------
// The 84 physical keys, CSV order (Full_84Key_Hole_Coordinates.csv, row 0 -> 5).
// keymap[ch] holds an INDEX into this table (-1 = unmapped). Names are what you
// Sharpie beside each landing hole -- log `cell . OUT . key`, then MAP it here.
const char* const KEY_NAMES[] = {
  "Esc","F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12",
  "PrtSc","Cust1","Cust2",
  "`","1","2","3","4","5","6","7","8","9","0","-","=","Bksp","nav-Home",
  "Tab","Q","W","E","R","T","Y","U","I","O","P","[","]","\\","nav-PgUp",
  "Caps","A","S","D","F","G","H","J","K","L",";","'","Enter","nav-PgDn",
  "LShift","Z","X","C","V","B","N","M",",",".","/","RShift","Up","nav-End",
  "LCtrl","LOpt","LCmd","Space","RCmd","Fn","RCtrl","Left","Down","Right"
};
const uint8_t NUM_KEYS = sizeof(KEY_NAMES) / sizeof(KEY_NAMES[0]);   // 84

int8_t keymap[NUM_CHANNELS];           // channel -> key index, -1 = unmapped

// shifted-symbol pairs: shifted char -> base key char (US/ANSI, Air75)
const char SHIFT_FROM[] = "!@#$%^&*()_+~{}|:\"<>?";
const char SHIFT_TO[]   = "1234567890-=`[]\\;',./";  // parallel to SHIFT_FROM

// ---- state ----------------------------------------------------------------------
uint8_t  shadow[NUM_CELLS];            // mirrors 595 outputs, [0] = cell #1
uint32_t lastFireEndMs = 0;
uint32_t lastFireEnd[NUM_CHANNELS];    // per-channel refire guard
uint32_t holdStart[NUM_CHANNELS];      // 0 = not held
uint32_t fireCount = 0;

// ---- shift-register core ----------------------------------------------------------
void writeShadow() {
  digitalWrite(PIN_LATCH, LOW);
#if CASCADE_REVERSED
  for (uint8_t c = 0; c < NUM_CELLS; c++)
    shiftOut(PIN_DATA, PIN_CLOCK, MSBFIRST, shadow[c]);
#else
  for (int8_t c = NUM_CELLS - 1; c >= 0; c--)   // cell 11 first, cell 1 last
    shiftOut(PIN_DATA, PIN_CLOCK, MSBFIRST, shadow[c]);
#endif
  digitalWrite(PIN_LATCH, HIGH);
}

uint8_t countOn() {
  uint8_t n = 0;
  for (uint8_t c = 0; c < NUM_CELLS; c++) {
    uint8_t b = shadow[c];
    while (b) { n += b & 1; b >>= 1; }
  }
  return n;
}

bool channelIsOn(uint8_t ch) {
  return shadow[ch >> 3] & (1 << (ch & 7));
}

// returns false if turning ON would exceed the simultaneous budget
bool setChannel(uint8_t ch, bool on) {
  if (ch >= NUM_CHANNELS) return false;
  if (on && !channelIsOn(ch) && countOn() >= MAX_ON) {
    Serial.print(F("ERR max ")); Serial.print(MAX_ON);
    Serial.println(F(" channels ON -- refused"));
    return false;
  }
  if (on) shadow[ch >> 3] |=  (1 << (ch & 7));
  else    shadow[ch >> 3] &= ~(1 << (ch & 7));
  writeShadow();
  return true;
}

void allOff() {
  for (uint8_t c = 0; c < NUM_CELLS; c++) shadow[c] = 0;
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) holdStart[i] = 0;
  writeShadow();
}

// ---- firing ---------------------------------------------------------------------------
// quiet actuation shared by FIRE/TYPE/KEY/CHORD/WALK (no serial chatter)
bool firePulse(uint8_t ch, uint16_t ms) {
  if (ch >= NUM_CHANNELS) return false;
  if (ms == 0)            ms = defaultPulseMs;
  if (ms > MAX_PULSE_MS)  ms = MAX_PULSE_MS;

  uint32_t now = millis();
  if (now - lastFireEndMs < MIN_GAP_MS)
    delay(MIN_GAP_MS - (now - lastFireEndMs));
  now = millis();
  if (now - lastFireEnd[ch] < REFIRE_MS)          // same-coil cooldown
    delay(REFIRE_MS - (now - lastFireEnd[ch]));

  if (!setChannel(ch, true)) return false;
  delay(ms);
  setChannel(ch, false);
  lastFireEndMs = lastFireEnd[ch] = millis();
  fireCount++;
  return true;
}

void cmdFire(uint8_t ch, uint16_t ms) {
  if (ch >= NUM_CHANNELS) {
    Serial.print(F("ERR bad channel ")); Serial.println(ch);
    return;
  }
  if (ms == 0)           ms = defaultPulseMs;
  if (ms > MAX_PULSE_MS) ms = MAX_PULSE_MS;
  if (firePulse(ch, ms)) {
    Serial.print(F("OK FIRE ")); Serial.print(ch);
    Serial.print(' '); Serial.println(ms);
  }
}

// ---- key lookup -------------------------------------------------------------------------
// case-insensitive string compare (names like "enter" should match "Enter")
bool nameEq(const char* a, const char* b) {
  while (*a && *b) {
    char ca = *a, cb = *b;
    if (ca >= 'A' && ca <= 'Z') ca += 32;
    if (cb >= 'A' && cb <= 'Z') cb += 32;
    if (ca != cb) return false;
    a++; b++;
  }
  return *a == 0 && *b == 0;
}

int findKeyByName(const char* name) {
  for (uint8_t i = 0; i < NUM_KEYS; i++)
    if (nameEq(name, KEY_NAMES[i])) return i;
  return -1;
}

int channelForKeyIndex(int8_t ki) {
  if (ki < 0) return -1;
  for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++)
    if (keymap[ch] == ki) return ch;
  return -1;
}

int channelForKeyName(const char* name) {
  return channelForKeyIndex(findKeyByName(name));
}

// ASCII char -> (base key name char/string, needs shift?)
// Returns key TABLE index via out param; true if resolvable.
bool asciiToKey(char c, int8_t &keyIdx, bool &shift) {
  shift = false;
  char base = 0;
  if (c >= 'a' && c <= 'z') { base = c - 32; }             // a -> "A"
  else if (c >= 'A' && c <= 'Z') { base = c; shift = true; }
  else if (c == ' ') { keyIdx = (int8_t)findKeyByName("Space"); return keyIdx >= 0; }
  else {
    // shifted symbols
    const char* p = strchr(SHIFT_FROM, c);
    if (p && c != 0) { base = SHIFT_TO[p - SHIFT_FROM]; shift = true; }
    else base = c;                                          // unshifted symbol row
  }
  // single-char key names: match directly
  char nm[2] = { base, 0 };
  keyIdx = (int8_t)findKeyByName(nm);
  return keyIdx >= 0;
}

// ---- typing -----------------------------------------------------------------------------
void typeText(const char* s) {
  if (typeLeadMs) {
    Serial.print(F("TYPE in ")); Serial.print(typeLeadMs);
    Serial.println(F(" ms -- click your target window now..."));
    delay(typeLeadMs);
  }
  int shiftCh = channelForKeyName("LShift");
  bool shiftHeld = false;
  Serial.print(F("OK TYPE "));
  for (const char* p = s; *p; p++) {
    int8_t ki; bool shift;
    if (!asciiToKey(*p, ki, shift)) { Serial.print('?'); continue; }
    int ch = channelForKeyIndex(ki);
    if (ch < 0) { Serial.print('?'); continue; }            // key not wired yet
    if (shift && shiftCh < 0) { Serial.print('?'); continue; } // no shift mapped
    // manage the shift chord across consecutive shifted chars
    if (shift && !shiftHeld) {
      if (!setChannel((uint8_t)shiftCh, true)) { Serial.print('!'); continue; }
      holdStart[shiftCh] = millis();
      shiftHeld = true;
      delay(CHORD_SEAT_MS);
    } else if (!shift && shiftHeld) {
      setChannel((uint8_t)shiftCh, false);
      holdStart[shiftCh] = 0;
      shiftHeld = false;
      delay(CHORD_SEAT_MS);
    }
    if (!firePulse((uint8_t)ch, defaultPulseMs)) { Serial.print('!'); continue; }
    delay(SETTLE_MS);
    Serial.print(*p);
  }
  if (shiftHeld) { setChannel((uint8_t)shiftCh, false); holdStart[shiftCh] = 0; }
  Serial.println();
}

// ---- chords --------------------------------------------------------------------------------
// CHORD LCmd+Space : hold every token but the last, fire the last, release reverse
void doChord(char* spec) {
  int8_t held[4]; uint8_t nHeld = 0;
  char* tok = strtok(spec, "+");
  char* next;
  int lastCh = -1;
  while (tok) {
    next = strtok(NULL, "+");
    int ch = channelForKeyName(tok);
    if (ch < 0) {
      Serial.print(F("ERR unknown/unmapped key: ")); Serial.println(tok);
      goto unwind;
    }
    if (next) {                                   // a modifier -> hold it
      if (nHeld >= 4 || !setChannel((uint8_t)ch, true)) goto unwind;
      holdStart[ch] = millis();
      held[nHeld++] = (int8_t)ch;
      delay(CHORD_SEAT_MS);
    } else {
      lastCh = ch;                                // the key itself
    }
    tok = next;
  }
  if (lastCh >= 0 && firePulse((uint8_t)lastCh, defaultPulseMs)) {
    delay(CHORD_SEAT_MS);
    Serial.println(F("OK CHORD"));
  }
unwind:
  while (nHeld > 0) {                             // release in reverse order
    nHeld--;
    setChannel((uint8_t)held[nHeld], false);
    holdStart[held[nHeld]] = 0;
    delay(10);
  }
}

// ---- walk mode ---------------------------------------------------------------------------------
void walk(int s, int e, int pulse, int gap) {
  if (s < 0) s = 0;
  if (e >= NUM_CHANNELS || e < 0) e = NUM_CHANNELS - 1;
  if (pulse <= 0) pulse = defaultPulseMs;
  if (gap < 200) gap = 200;
  Serial.print(F("OK WALK ")); Serial.print(s);
  Serial.print(F("..")); Serial.print(e);
  Serial.println(F("  (any key aborts)"));
  for (int ch = s; ch <= e; ch++) {
    if (Serial.available()) {
      while (Serial.available()) Serial.read();
      Serial.println(F("WALK aborted"));
      return;
    }
    Serial.print(F("WALK ch ")); Serial.print(ch);
    Serial.print(F("  cell ")); Serial.print(ch / 8 + 1);
    Serial.print(F(" OUT")); Serial.print(ch % 8 + 1);
    if (keymap[ch] >= 0) {
      Serial.print(F("  -> ")); Serial.print(KEY_NAMES[(uint8_t)keymap[ch]]);
    }
    Serial.println();
    firePulse((uint8_t)ch, (uint16_t)pulse);
    delay(gap);
  }
  Serial.println(F("WALK done"));
}

// ---- keymap + EEPROM ------------------------------------------------------------------------------
void printMap() {
  Serial.println(F("MAP (ch cell/OUT key):"));
  for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++) {
    if (keymap[ch] < 0) continue;
    Serial.print(F("  ")); Serial.print(ch);
    Serial.print(F("  c")); Serial.print(ch / 8 + 1);
    Serial.print(F("/OUT")); Serial.print(ch % 8 + 1);
    Serial.print(F("  ")); Serial.println(KEY_NAMES[(uint8_t)keymap[ch]]);
  }
  uint8_t n = 0;
  for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++) if (keymap[ch] >= 0) n++;
  Serial.print(n); Serial.print('/'); Serial.print(NUM_KEYS);
  Serial.println(F(" keys mapped"));
}

const uint16_t EE_MAGIC = 0x4B31;   // 'K1'
void saveMap() {
  uint16_t addr = 0;
  EEPROM.update(addr++, EE_MAGIC >> 8);
  EEPROM.update(addr++, EE_MAGIC & 0xFF);
  uint8_t sum = 0;
  for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++) {
    uint8_t v = (keymap[ch] < 0) ? 0xFF : (uint8_t)keymap[ch];
    EEPROM.update(addr++, v);
    sum ^= v;
  }
  EEPROM.update(addr, sum);
  Serial.println(F("OK SAVE"));
}

bool loadMap(bool verbose) {
  uint16_t addr = 0;
  if (EEPROM.read(addr++) != (EE_MAGIC >> 8) ||
      EEPROM.read(addr++) != (EE_MAGIC & 0xFF)) {
    if (verbose) Serial.println(F("ERR no saved map"));
    return false;
  }
  uint8_t sum = 0; int8_t tmp[NUM_CHANNELS];
  for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++) {
    uint8_t v = EEPROM.read(addr++);
    sum ^= v;
    tmp[ch] = (v == 0xFF || v >= NUM_KEYS) ? -1 : (int8_t)v;
  }
  if (EEPROM.read(addr) != sum) {
    if (verbose) Serial.println(F("ERR map checksum"));
    return false;
  }
  memcpy(keymap, tmp, NUM_CHANNELS);
  if (verbose) Serial.println(F("OK LOAD"));
  return true;
}

// ---- hold / release ----------------------------------------------------------------------------------
int resolveChannelArg(const char* a) {           // "<name>" or "<number>"
  if (a[0] >= '0' && a[0] <= '9') {
    int ch = atoi(a);
    return (ch >= 0 && ch < NUM_CHANNELS) ? ch : -1;
  }
  return channelForKeyName(a);
}

void serviceHoldTimeouts() {
  uint32_t now = millis();
  for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++) {
    if (holdStart[ch] && now - holdStart[ch] > MAX_HOLD_MS) {
      setChannel(ch, false);
      holdStart[ch] = 0;
      Serial.print(F("WARN auto-release ch ")); Serial.println(ch);
    }
  }
}

// ---- speed test (320 WPM GO/NO-GO) ------------------------------------------------------
// REPEAT <ch> <pulse> <period> <count>: fire ONE channel <count> times, a new
// pulse starting every <period> ms. Bypasses REFIRE_MS on purpose -- this is
// the test that measures it. Put the coil over a key in a text editor and
// count the characters: count typed == count sent -> that period is reliable.
// Limits: pulse 2..50 ms, period >= pulse+3, count 1..60. Any serial input aborts.
void repeatTest(int ch, int pulse, int period, int count) {
  if (ch < 0 || ch >= NUM_CHANNELS) { Serial.println(F("ERR bad channel")); return; }
  if (pulse < 2) pulse = 2;
  if (pulse > 50) pulse = 50;
  if (period < pulse + 3) period = pulse + 3;
  if (count < 1) count = 1;
  if (count > 60) count = 60;
  Serial.print(F("OK REPEAT ch ")); Serial.print(ch);
  Serial.print(F(" pulse=")); Serial.print(pulse);
  Serial.print(F(" period=")); Serial.print(period);
  Serial.print(F(" count=")); Serial.print(count);
  Serial.print(F("  (= ")); Serial.print(12000L / period);
  Serial.println(F(" WPM if every key took this long)"));
  delay(typeLeadMs);
  uint32_t t0 = millis();
  for (int i = 0; i < count; i++) {
    if (Serial.available()) { allOff(); Serial.println(F("REPEAT aborted")); return; }
    uint32_t start = t0 + (uint32_t)i * period;
    while ((int32_t)(millis() - start) < 0) {}
    setChannel((uint8_t)ch, true);
    delay(pulse);
    setChannel((uint8_t)ch, false);
    fireCount++;
  }
  lastFireEndMs = lastFireEnd[ch] = millis();
  Serial.print(F("REPEAT done in ")); Serial.print(millis() - t0);
  Serial.println(F(" ms -- now count the characters"));
}

// ---- fast-TYPE stream scheduler (brief 09) ----------------------------------------------
// Timeline rules, per char, in queue order:
//   due = max( base slot,                         base advances 1 interval/char
//              prev key-down + STREAM_STAGGER_US, keeps key-down ORDER on the Nuphy
//              this coil's last start + SAMEKEY ) double letters (coil must return)
// A same-key delay pushes only that char; the base timeline is kept, so the next
// char is back on schedule. Empty queue at a due slot = underrun: when text
// arrives the timeline restarts from "now" (no burst to catch up).
const uint16_t SQ_SIZE  = 1024;                  // power of 2
const uint16_t SQ_MASK  = SQ_SIZE - 1;
const uint32_t STREAM_STAGGER_US = 10000;        // min start-to-start, different keys (UNVERIFIED)
const uint32_t STREAM_STARVE_TIMEOUT_MS = 3000;  // no END and nothing to type -> finish
const uint32_t STREAM_MAX_MS = 120000;           // hard cap on one run

char     sq[SQ_SIZE];
uint16_t sqHead = 0, sqTail = 0;                 // free-running indices
inline uint16_t sqCount() { return (uint16_t)(sqTail - sqHead); }
inline uint16_t sqFree()  { return SQ_SIZE - sqCount(); }

uint16_t sWpm      = 330;
uint32_t sIntervalUs = 12000000UL / 330;
uint16_t sPulseMs  = 20;
uint16_t sSameMs   = 45;

enum StreamState : uint8_t { S_IDLE, S_LEAD, S_RUN };
StreamState sState = S_IDLE;
bool     sEnded = false, sStarved = false;
uint32_t sLeadEndMs = 0, sStartMs = 0, sStarveMs = 0;
uint32_t sNextDueUs = 0, sPrevStartUs = 0, sFirstUs = 0, sLastUs = 0;
uint32_t sChStartUs[NUM_CHANNELS];               // last key-down per coil (this run)
int8_t   sLut[128];                              // char -> ch; -1 unmapped, -2 needs shift
struct ActivePulse { uint8_t ch; uint32_t offUs; };
ActivePulse sAct[MAX_ON];
uint8_t  sNAct = 0;
// stats
uint16_t stSlots, stFired, stSkipped, stShift, stSame, stUnder;
uint32_t stLateMaxUs;

inline bool usAfter(uint32_t a, uint32_t b) { return (int32_t)(a - b) > 0; }  // a later than b

void streamSetWpm(int w) {
  if (w < 30) w = 30;
  if (w > 1000) w = 1000;              // Oct 5: was 600 (541 result); 10 ms stagger allows ~1200
  sWpm = (uint16_t)w;
  sIntervalUs = 12000000UL / (uint32_t)w;
}

void buildLut() {
  for (uint8_t c = 0; c < 128; c++) {
    sLut[c] = -1;
    if (c < 0x20 || c > 0x7E) continue;
    int8_t ki; bool shift;
    if (!asciiToKey((char)c, ki, shift)) continue;
    if (shift) { sLut[c] = -2; continue; }
    int ch = channelForKeyIndex(ki);
    if (ch >= 0) sLut[c] = (int8_t)ch;
  }
}

bool streamBusy() { return sState != S_IDLE; }

// append text verbatim; returns false (nothing appended) if it doesn't fit
bool streamEnqueue(const char* t) {
  uint16_t n = strlen(t);
  if (n > sqFree()) return false;
  for (uint16_t i = 0; i < n; i++) sq[(sqTail++) & SQ_MASK] = t[i];
  return true;
}

void streamGo() {
  buildLut();
  uint32_t now = micros();
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) sChStartUs[i] = now - 10000000UL;
  sPrevStartUs = now - 10000000UL;
  stSlots = stFired = stSkipped = stShift = stSame = stUnder = 0;
  stLateMaxUs = 0;
  sNAct = 0;
  sStarved = false;
  sStartMs = millis();
  sLeadEndMs = sStartMs + typeLeadMs;
  sState = S_LEAD;
  Serial.print(F("OK GO in ")); Serial.print(typeLeadMs);
  Serial.print(F(" ms  wpm=")); Serial.print(sWpm);
  Serial.print(F(" pulse=")); Serial.print(sPulseMs);
  Serial.print(F(" same=")); Serial.print(sSameMs);
  Serial.print(F(" queued=")); Serial.println(sqCount());
}

void streamFinish(const __FlashStringHelper* why) {
  // force every stream pulse off (held channels untouched unless STOP/ALLOFF)
  for (uint8_t i = 0; i < sNAct; i++) {
    shadow[sAct[i].ch >> 3] &= ~(1 << (sAct[i].ch & 7));
    lastFireEnd[sAct[i].ch] = millis();
  }
  sNAct = 0;
  writeShadow();
  lastFireEndMs = millis();
  sState = S_IDLE;
  sEnded = false;
  uint32_t span = (stSlots > 0) ? (sLastUs - sFirstUs + sIntervalUs) : 0;
  Serial.print(F("DONE ")); Serial.print(why);
  Serial.print(F(" slots=")); Serial.print(stSlots);
  Serial.print(F(" fired=")); Serial.print(stFired);
  Serial.print(F(" skipped=")); Serial.print(stSkipped);
  Serial.print(F(" shift=")); Serial.print(stShift);
  Serial.print(F(" same=")); Serial.print(stSame);
  Serial.print(F(" under=")); Serial.print(stUnder);
  Serial.print(F(" lateMax=")); Serial.print(stLateMaxUs);
  Serial.print(F("us ms=")); Serial.print(span / 1000);
  Serial.print(F(" wpm="));
  if (span > 0) Serial.println((float)stSlots * 12000000.0f / (float)span, 1);
  else Serial.println(0);
  Serial.print(F("K ")); Serial.println(sqFree());
}

void streamStop() {
  bool wasBusy = streamBusy();
  sEnded = false;
  sqHead = sqTail;                                // drop the queue
  if (wasBusy) streamFinish(F("stopped"));
  else { Serial.print(F("OK STOP  K ")); Serial.println(sqFree()); }
}

// one slot consumed (fired or silent): advance the base timeline
void slotDone(uint32_t now) {
  if (stSlots == 0) sFirstUs = now;
  stSlots++;
  sLastUs = now;
  sNextDueUs += sIntervalUs;
  if (usAfter(now, sNextDueUs)) sNextDueUs = now; // >1 slot behind: no catch-up burst
}

// call as often as possible (loop + between serial bytes); never blocks
void streamService() {
  if (sState == S_IDLE) return;
  uint32_t nowMs = millis();
  if (sState == S_LEAD) {
    if ((int32_t)(nowMs - sLeadEndMs) < 0) return;
    sState = S_RUN;
    sNextDueUs = micros();
  }
  if (nowMs - sStartMs > STREAM_MAX_MS) { sqHead = sqTail; streamFinish(F("maxtime")); return; }

  uint32_t now = micros();
  bool dirty = false;

  // 1) end expired pulses
  for (uint8_t i = 0; i < sNAct; ) {
    if (!usAfter(sAct[i].offUs, now)) {
      uint8_t ch = sAct[i].ch;
      shadow[ch >> 3] &= ~(1 << (ch & 7));
      lastFireEnd[ch] = nowMs;
      fireCount++;
      sAct[i] = sAct[--sNAct];
      dirty = true;
    } else i++;
  }

  // 2) next char
  if (sqCount() > 0) {
    if (sStarved) { sStarved = false; sNextDueUs = now; }   // restart timeline after underrun
    char c = sq[sqHead & SQ_MASK];
    int8_t ch = ((uint8_t)c < 128) ? sLut[(uint8_t)c] : -1;
    if (ch < 0) {                                          // silent slot
      if (!usAfter(sNextDueUs, now)) {
        sqHead++;
        if (ch == -2) stShift++; else stSkipped++;
        slotDone(now);
      }
    } else {
      uint32_t due = sNextDueUs;
      bool sameHit = false;
      uint32_t t = sPrevStartUs + STREAM_STAGGER_US;
      if (usAfter(t, due)) due = t;
      t = sChStartUs[ch] + (uint32_t)sSameMs * 1000UL;
      if (usAfter(t, due)) { due = t; sameHit = true; }
      bool coilBusy = channelIsOn((uint8_t)ch);            // still on (or HELD)
      if (!usAfter(due, now) && !coilBusy && sNAct < MAX_ON && countOn() < MAX_ON) {
        shadow[ch >> 3] |= (1 << (ch & 7));
        dirty = true;
        sAct[sNAct].ch = (uint8_t)ch;
        sAct[sNAct].offUs = now + (uint32_t)sPulseMs * 1000UL;
        sNAct++;
        sqHead++;
        uint32_t late = now - due;
        if (late > stLateMaxUs) stLateMaxUs = late;
        if (sameHit) stSame++;
        stFired++;
        sChStartUs[ch] = now;
        sPrevStartUs = now;
        slotDone(now);
      }
    }
  } else if (sState == S_RUN) {
    // 3) nothing queued
    if (!sStarved && !usAfter(sNextDueUs, now)) {
      sStarved = true;
      sStarveMs = nowMs;
      if (stSlots > 0 && !sEnded) stUnder++;
    }
    if (dirty) { writeShadow(); dirty = false; }
    if (sNAct == 0) {
      if (sEnded) { streamFinish(F("end")); return; }
      if (sStarved && nowMs - sStarveMs > STREAM_STARVE_TIMEOUT_MS) {
        streamFinish(F("timeout")); return;
      }
    }
  }
  if (dirty) writeShadow();
}


// ---- status ----------------------------------------------------------------------------------------------
void printStatus() {
  Serial.print(F("STATUS pulse=")); Serial.print(defaultPulseMs);
  Serial.print(F("ms lead=")); Serial.print(typeLeadMs);
  Serial.print(F("ms fires=")); Serial.print(fireCount);
  Serial.print(F(" on=")); Serial.print(countOn());
  uint8_t n = 0;
  for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++) if (keymap[ch] >= 0) n++;
  Serial.print(F(" mapped=")); Serial.print(n);
  Serial.print('/'); Serial.println(NUM_KEYS);
  Serial.print(F("  stream ")); Serial.print(streamBusy() ? F("RUNNING") : F("idle"));
  Serial.print(F(" wpm=")); Serial.print(sWpm);
  Serial.print(F(" fpulse=")); Serial.print(sPulseMs);
  Serial.print(F(" samekey=")); Serial.print(sSameMs);
  Serial.print(F(" queued=")); Serial.print(sqCount());
  Serial.print(F(" free=")); Serial.println(sqFree());
  for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++)
    if (holdStart[ch]) {
      Serial.print(F("  held: ch ")); Serial.println(ch);
    }
}

// ---- serial parser ------------------------------------------------------------------------------------------
char    buf[200];                      // Q lines from the reader are <= 120 chars
uint8_t bufLen = 0;

// true if line is exactly <cmd> or <cmd> followed by a space
bool isCmd(const char* line, const char* cmd) {
  size_t n = strlen(cmd);
  return strncmp(line, cmd, n) == 0 && (line[n] == ' ' || line[n] == 0);
}

// stream + tuning commands; returns true if the line was one of them
bool handleStreamLine(char* line) {
  if (line[0] == 'Q' && line[1] == ' ') {               // Q <text>, verbatim
    if (!streamEnqueue(line + 2)) {
      Serial.print(F("ERR qfull K ")); Serial.println(sqFree());
    } else { Serial.print(F("K ")); Serial.println(sqFree()); }
    return true;
  }
  if (isCmd(line, "GO")) {
    if (streamBusy()) Serial.println(F("ERR already running"));
    else streamGo();                                  // an END sent earlier still counts
    return true;
  }
  if (isCmd(line, "END")) {
    sEnded = true;
    Serial.println(F("OK END"));
    return true;
  }
  if (isCmd(line, "STOP")) { streamStop(); return true; }
  if (isCmd(line, "FAST")) {
    if (streamBusy()) { Serial.println(F("ERR busy (STOP first)")); return true; }
    const char* txt = line + 4;
    if (*txt == ' ') txt++;                              // keep any further spaces
    if (*txt == 0) { Serial.println(F("ERR usage: FAST <text>")); return true; }
    sqHead = sqTail;
    streamEnqueue(txt);
    streamGo();
    sEnded = true;
    return true;
  }
  if (isCmd(line, "WPM")) {
    int w = -1;
    if (sscanf(line + 3, "%d", &w) == 1 && w > 0) streamSetWpm(w);
    Serial.print(F("WPM ")); Serial.print(sWpm);
    Serial.print(F(" (")); Serial.print(sIntervalUs); Serial.println(F(" us/char)"));
    return true;
  }
  if (isCmd(line, "FPULSE")) {
    int ms = -1;
    if (sscanf(line + 6, "%d", &ms) == 1 && ms > 0) {
      if (ms < 5) ms = 5;
      if (ms > 50) ms = 50;
      sPulseMs = (uint16_t)ms;
    }
    Serial.print(F("FPULSE ")); Serial.println(sPulseMs);
    return true;
  }
  if (isCmd(line, "SAMEKEY")) {
    int ms = -1;
    if (sscanf(line + 7, "%d", &ms) == 1 && ms > 0) {
      if (ms < 20) ms = 20;
      if (ms > 200) ms = 200;
      sSameMs = (uint16_t)ms;
    }
    Serial.print(F("SAMEKEY ")); Serial.println(sSameMs);
    return true;
  }
  return false;
}

void handleLine(char* line) {
  if (handleStreamLine(line)) return;
  if (streamBusy()) {                                  // only safe commands mid-run
    if (strcmp(line, "STATUS") == 0) { printStatus(); return; }
    if (strcmp(line, "ALLOFF") == 0) { sqHead = sqTail; streamFinish(F("alloff")); allOff(); return; }
    if (line[0] != 0) Serial.println(F("ERR busy (STOP first)"));
    return;
  }
  if (strncmp(line, "FIRE", 4) == 0) {
    int ch = -1, ms = -1;
    int n = sscanf(line + 4, "%d %d", &ch, &ms);
    if (n >= 1 && ch >= 0) cmdFire((uint8_t)ch, (n >= 2 && ms > 0) ? (uint16_t)ms : 0);
    else Serial.println(F("ERR usage: FIRE <ch> [ms]"));

  } else if (strncmp(line, "PULSE", 5) == 0) {
    int ms = -1;
    if (sscanf(line + 5, "%d", &ms) == 1 && ms > 0) {
      if (ms > MAX_PULSE_MS) ms = MAX_PULSE_MS;
      defaultPulseMs = (uint16_t)ms;
      Serial.print(F("OK PULSE ")); Serial.println(defaultPulseMs);
    } else { Serial.print(F("PULSE ")); Serial.println(defaultPulseMs); }

  } else if (strncmp(line, "WALK", 4) == 0) {
    int s = 0, e = NUM_CHANNELS - 1, p = 0, g = 800;
    sscanf(line + 4, "%d %d %d %d", &s, &e, &p, &g);
    walk(s, e, p, g);

  } else if (strncmp(line, "TYPE", 4) == 0) {
    const char* txt = line + 4;
    while (*txt == ' ') txt++;
    if (*txt == 0) Serial.println(F("ERR usage: TYPE <text>"));
    else typeText(txt);

  } else if (strncmp(line, "KEY", 3) == 0 && (line[3] == ' ' || line[3] == 0)) {
    char name[16] = {0};
    if (sscanf(line + 3, "%15s", name) == 1) {
      int ch = channelForKeyName(name);
      if (ch < 0) { Serial.print(F("ERR unknown/unmapped key: ")); Serial.println(name); }
      else if (firePulse((uint8_t)ch, defaultPulseMs)) {
        Serial.print(F("OK KEY ")); Serial.println(name);
      }
    } else Serial.println(F("ERR usage: KEY <name>"));

  } else if (strncmp(line, "CHORD", 5) == 0) {
    char* spec = line + 5;
    while (*spec == ' ') spec++;
    if (*spec == 0) Serial.println(F("ERR usage: CHORD <a>+<b>[+<c>]"));
    else doChord(spec);

  } else if (strncmp(line, "HOLD", 4) == 0) {
    char name[16] = {0};
    if (sscanf(line + 4, "%15s", name) == 1) {
      int ch = resolveChannelArg(name);
      if (ch < 0) Serial.println(F("ERR unknown key/channel"));
      else if (setChannel((uint8_t)ch, true)) {
        holdStart[ch] = millis();
        Serial.print(F("OK HOLD ch ")); Serial.println(ch);
      }
    } else Serial.println(F("ERR usage: HOLD <name|ch>"));

  } else if (strncmp(line, "RELEASE", 7) == 0) {
    char name[16] = {0};
    if (sscanf(line + 7, "%15s", name) == 1) {
      if (nameEq(name, "ALL")) { allOff(); Serial.println(F("OK RELEASE ALL")); }
      else {
        int ch = resolveChannelArg(name);
        if (ch < 0) Serial.println(F("ERR unknown key/channel"));
        else {
          setChannel((uint8_t)ch, false);
          holdStart[ch] = 0;
          Serial.print(F("OK RELEASE ch ")); Serial.println(ch);
        }
      }
    } else Serial.println(F("ERR usage: RELEASE <name|ch|ALL>"));

  } else if (strncmp(line, "MAP", 3) == 0) {
    int ch = -1; char name[16] = {0};
    if (sscanf(line + 3, "%d %15s", &ch, name) == 2 && ch >= 0 && ch < NUM_CHANNELS) {
      if (strcmp(name, "-") == 0) {
        keymap[ch] = -1;
        Serial.print(F("OK MAP ")); Serial.print(ch); Serial.println(F(" cleared"));
      } else {
        int ki = findKeyByName(name);
        // "-" alone means "clear", so the minus key is mapped as "Minus"
        if (ki < 0 && (strcmp(name, "Minus") == 0 || strcmp(name, "minus") == 0))
          ki = findKeyByName("-");
        if (ki < 0) { Serial.print(F("ERR unknown key name: ")); Serial.println(name); }
        else {
          int prev = channelForKeyIndex((int8_t)ki);
          if (prev >= 0 && prev != ch) {
            Serial.print(F("WARN ")); Serial.print(KEY_NAMES[ki]);
            Serial.print(F(" was on ch ")); Serial.print(prev);
            Serial.println(F(" -- cleared"));
            keymap[prev] = -1;
          }
          keymap[ch] = (int8_t)ki;
          Serial.print(F("OK MAP ")); Serial.print(ch);
          Serial.print(' '); Serial.println(KEY_NAMES[ki]);
        }
      }
    } else printMap();

  } else if (strcmp(line, "SAVE") == 0) { saveMap();
  } else if (strcmp(line, "LOAD") == 0) { loadMap(true);
  } else if (strncmp(line, "LEAD", 4) == 0) {
    int ms = -1;
    if (sscanf(line + 4, "%d", &ms) == 1 && ms >= 0) {
      if (ms > 10000) ms = 10000;
      typeLeadMs = (uint16_t)ms;
      Serial.print(F("OK LEAD ")); Serial.println(typeLeadMs);
    } else { Serial.print(F("LEAD ")); Serial.println(typeLeadMs); }

  } else if (strncmp(line, "REPEAT", 6) == 0) {
    int ch = -1, p = 0, per = 0, n = 0;
    if (sscanf(line + 6, "%d %d %d %d", &ch, &p, &per, &n) == 4) repeatTest(ch, p, per, n);
    else Serial.println(F("ERR usage: REPEAT <ch> <pulse> <period> <count>"));

  } else if (strcmp(line, "STATUS") == 0) { printStatus();
  } else if (strcmp(line, "ALLOFF") == 0) {
    allOff();
    Serial.println(F("OK ALLOFF"));
  } else if (line[0] != 0) {
    Serial.print(F("ERR unknown: ")); Serial.println(line);
  }
}

void setup() {
  pinMode(PIN_DATA, OUTPUT);
  pinMode(PIN_CLOCK, OUTPUT);
  pinMode(PIN_LATCH, OUTPUT);
  if (PIN_OE != 255) {                 // OE mod installed: outputs still disabled
    pinMode(PIN_OE, OUTPUT);
    digitalWrite(PIN_OE, HIGH);
  }
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
    keymap[i] = -1;
    lastFireEnd[i] = 0;
    holdStart[i] = 0;
  }
  allOff();                            // clear all 11 registers FIRST
  if (PIN_OE != 255) digitalWrite(PIN_OE, LOW);   // ...then enable outputs
  Serial.begin(115200);
  bool loaded = loadMap(false);        // restore keymap if one was saved
  Serial.print(F("keyboard_v1 ready  cells=")); Serial.print(NUM_CELLS);
  Serial.print(F(" pulse=")); Serial.print(defaultPulseMs);
  Serial.print(F("ms map=")); Serial.println(loaded ? F("EEPROM") : F("empty"));
  Serial.println(F("cmds: FIRE PULSE WALK TYPE KEY CHORD HOLD RELEASE MAP SAVE LOAD LEAD REPEAT STATUS ALLOFF"));
  Serial.println(F("fast: Q GO END FAST STOP WPM FPULSE SAMEKEY"));
}

// Oct 5 2026 safety net: noise on CLK/LATCH can latch random coils ON and,
// with the firmware idle, they stayed ON for minutes (pop + smoke incident).
// Re-assert the intended state (shadow[]) every REFRESH_MS while no stream runs,
// so any glitch is overwritten within a few ms. Costs ~1.3 ms per refresh.
const uint16_t REFRESH_MS = 5;
uint32_t lastRefreshMs = 0;
void refreshRegisters() {
  if (streamBusy()) return;                 // stream rewrites shadow itself
  uint32_t now = millis();
  if (now - lastRefreshMs >= REFRESH_MS) { lastRefreshMs = now; writeShadow(); }
}

void loop() {
  refreshRegisters();
  streamService();
  while (Serial.available()) {
    streamService();                   // keep the schedule alive between bytes
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
  serviceHoldTimeouts();
}
