#include <Arduino.h>

void setup() {
  pinMode(A15, OUTPUT);
}

void loop() {
  digitalWrite(A15, HIGH);
  sleep(1);
  digitalWrite(A15, LOW);
  sleep(1);
}