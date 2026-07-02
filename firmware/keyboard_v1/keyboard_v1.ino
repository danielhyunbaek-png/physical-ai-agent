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
//   With OE hard-wired to GND, all 11 595s output RANDOM data from power-up
//   until setup() clears them. On 84 solenoids that's potential random 12V
//   pulses at every boot. Operating rule: BRING UP THE ARDUINO (USB) FIRST,
//   THEN switch on the 12V rail. Hardware fix if it ever bites: lift OE from
//   GND, add 10k pullup to +5V, run OE to a Mega pin, define PIN_OE below --
//   firmware then holds outputs disabled until the registers are cleared.
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
//   STATUS                  pulse, lead, mapped count, held channels, fire count
//   ALLOFF                  force every channel low
//
// Wiring per cell is unchanged from keyboard_v0 / OneCell guide:
//   595: DS<-prev(or D11), SH_CP=D12 (bused), ST_CP=D13 (bused), OE=GND, MR=+5V
//   ULN: IN1-8 <- Q0-7 canonical, COM(10) -> +12V (flyback -- never skip),
//        GND(9) -> star ground. 0.1uF per chip, bulk cap on the 12V rail.

#include <EEPROM.h>

// ---- pins -------------------------------------------------------------------
const uint8_t PIN_DATA  = 11;   // 595 DS (cell #1)
const uint8_t PIN_CLOCK = 12;   // 595 SH_CP (bused to all cells)
const uint8_t PIN_LATCH = 13;   // 595 ST_CP (bused to all cells)
const uint8_t PIN_OE    = 255;  // 255 = OE hard-wired to GND (as-built).
                                // Set to a real pin if the pullup mod is done.
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
  for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++)
    if (holdStart[ch]) {
      Serial.print(F("  held: ch ")); Serial.println(ch);
    }
}

// ---- serial parser ------------------------------------------------------------------------------------------
char    buf[128];
uint8_t bufLen = 0;

void handleLine(char* line) {
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
  Serial.println(F("cmds: FIRE PULSE WALK TYPE KEY CHORD HOLD RELEASE MAP SAVE LOAD LEAD STATUS ALLOFF"));
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
  serviceHoldTimeouts();
}
