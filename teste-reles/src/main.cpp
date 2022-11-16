#include <Arduino.h>

void setup() {
  pinMode(15, OUTPUT);
}

void loop() {
  digitalWrite(15, HIGH);
  sleep(1);
  digitalWrite(15, LOW);
  sleep(1);
}