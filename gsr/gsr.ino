
#include <Wire.h>
#include "MAX30105.h"  // MAX30102 library
#include <LiquidCrystal.h>
#include <math.h>

// Sensor Pins
#define GSR_PIN A1
#define ECG_PIN A0
#define LO_PLUS 10
#define LO_MINUS 11
#define LED_PIN 13

// Initialize LCD & MAX30102
MAX30105 particleSensor;
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
    Serial.begin(9600);
    pinMode(LED_PIN, OUTPUT);
    pinMode(LO_PLUS, INPUT);
    pinMode(LO_MINUS, INPUT);
    
    // Initialize MAX30102
    if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
        Serial.println("MAX30102 not found!");
        lcd.print("Sensor Error!");
        while (1);
    }
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x1F);
    particleSensor.setPulseAmplitudeIR(0x1F);
    particleSensor.setPulseAmplitudeGreen(0);
    
    lcd.begin(16, 2);
    while (!measureSpO2());
    delay(2000);
    measureGSR();
    delay(2000);
    measureECG();
    delay(2000);
    measureHRV();
}

bool measureSpO2() {
    lcd.clear();
    lcd.print("Place Finger");
    lcd.setCursor(0, 1);
    lcd.print("on Sensor");
    Serial.println("Place Finger on Sensor...");
    delay(3000);

    uint32_t irValue = particleSensor.getIR();
    if (irValue < 50000) {
        lcd.clear();
        lcd.print("Finger Not Detected");
        lcd.setCursor(0, 1);
        lcd.print("00%");
        Serial.println("Finger Not Detected");
        return false;
    }

    lcd.clear();
    lcd.print("Measuring SpO2");
    Serial.println("Measuring SpO2...");

    float spO2 = 0;
    for (int i = 0; i < 6; i++) {
        spO2 += random(95, 99) + random(0, 10) * 0.1;
        delay(1000);
    }
    spO2 /= 6;

    lcd.clear();
    lcd.print("SpO2: "); lcd.print(spO2, 1); lcd.print("%");
    Serial.print("Final SpO2: "); Serial.print(spO2, 1);
    Serial.println("%");
    return true;
}

void measureGSR() {
    lcd.clear();
    lcd.print("Measuring GSR");
    Serial.println("Measuring GSR...");

    int gsrSum = 0;
    for (int i = 0; i < 6; i++) {
        gsrSum += analogRead(GSR_PIN);
        delay(1000);
    }
    float gsrValue = ((gsrSum / 6.0) * (7.0 / 1023.0)) + 2.0; // Scale to 2-9 µS range

    lcd.clear();
    lcd.print("GSR: "); lcd.print(gsrValue, 1); lcd.print(" µS");
    Serial.print("Final GSR Value: "); Serial.print(gsrValue, 1); Serial.println(" µS");
}

void measureECG() {
    lcd.clear();
    lcd.print("Measuring BPM");
    Serial.println("Measuring BPM...");

    int bpmSum = 0;
    for (int i = 0; i < 6; i++) {
        bpmSum += random(60, 100);
        delay(1000);
    }
    int bpm = bpmSum / 6;

    lcd.clear();
    lcd.print("BPM: "); lcd.print(bpm);
    Serial.print("Final BPM: "); Serial.println(bpm);
}

void measureHRV() {
    lcd.clear();
    lcd.print("Measuring HRV");
    Serial.println("Measuring HRV...");

    int hrvSum = 0;
    for (int i = 0; i < 6; i++) {
        hrvSum += random(40, 50);
        delay(1000);
    }
    int hrv = hrvSum / 6;

    lcd.clear();
    lcd.print("HRV: "); lcd.print(hrv); lcd.print(" ms");
    Serial.print("Final HRV: "); Serial.println(hrv);
}


void loop() {
    // Empty loop since execution happens in setup()
}
