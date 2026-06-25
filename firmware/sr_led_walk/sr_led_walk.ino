// sr_led_walk.ino
// Week 2 step 1: walk a single bit across the 8 outputs of one 74HC595.
// Wire 8 LEDs (with ~330 ohm series resistors) from Q0..Q7 to GND.
//
// Wiring (74HC595 -> Arduino Mega):
//   DS    (pin 14) -> D11   (data)
//   SH_CP (pin 11) -> D12   (shift clock)
//   ST_CP (pin 12) -> D13   (latch / storage clock)
//   OE    (pin 13) -> GND   (always enable outputs)
//   MR    (pin 10) -> +5V   (don't reset)
//   VCC   (pin 16) -> +5V
//   GND   (pin  8) -> GND
//   Q0..Q7 (pins 15, 1..7) -> LEDs -> GND
//
// Decoupling: 0.1 uF cap across VCC/GND of the 595, close to the chip.

const uint8_t PIN_DATA  = 11;  // DS
const uint8_t PIN_CLOCK = 12;  // SH_CP
const uint8_t PIN_LATCH = 13;  // ST_CP

void writeByte(uint8_t b) {
  digitalWrite(PIN_LATCH, LOW);
  shiftOut(PIN_DATA, PIN_CLOCK, MSBFIRST, b);
  digitalWrite(PIN_LATCH, HIGH);
}

void setup() {
  pinMode(PIN_DATA, OUTPUT);
  pinMode(PIN_CLOCK, OUTPUT);
  pinMode(PIN_LATCH, OUTPUT);
  writeByte(0x00);
  Serial.begin(115200);
  Serial.println(F("sr_led_walk ready"));
}

void loop() {
  for (uint8_t i = 0; i < 8; i++) {
    writeByte(1 << i);
    delay(150);
  }
  writeByte(0x00);
  delay(300);
}
