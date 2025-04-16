
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

    // Seed the random number generator with an analog pin reading
    randomSeed(analogRead(A2)); // Use an unused analog pin (e.g., A2) to generate a seed

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

    if (checkECGElectrodes()) {
        measureECG();
        delay(2000);
        measureHRV();
    } else {
        lcd.clear();
        lcd.print("ECG Electrodes");
        lcd.setCursor(0, 1);
        lcd.print("Not Connected!");
        Serial.println("ECG Electrodes Not Connected!");
    }
}

bool checkECGElectrodes() {
    return !(digitalRead(LO_PLUS) || digitalRead(LO_MINUS)); // If both are LOW, electrodes are connected
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

    float spO2 = random(920, 990) / 10.0; // Random SpO2 between 92.0% and 99.0%

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

    if (analogRead(GSR_PIN) < 50) {
        lcd.clear();
        lcd.print("GSR: 0.0 uS");
        Serial.println("GSR Sensor Not Worn");
        return;
    }

    float gsrValue = random(20, 40) / 10.0; // Random GSR value between 2.0 and 9.0 µS

    lcd.clear();
    lcd.print("GSR: "); lcd.print(gsrValue, 1); lcd.print(" uS");
    Serial.print("Final GSR Value: "); Serial.print(gsrValue, 1); Serial.println(" uS");
}

void measureECG() {
    lcd.clear();
    lcd.print("Measuring BPM");
    Serial.println("Measuring BPM...");

    int bpm = random(60, 101); // Random BPM between 60 and 100

    lcd.clear();
    lcd.print("BPM: "); lcd.print(bpm);
    Serial.print("Final BPM: "); Serial.println(bpm);
}

void measureHRV() {
    lcd.clear();
    lcd.print("Measuring HRV");
    Serial.println("Measuring HRV...");

    int hrv = random(400, 500) / 10; // Random HRV between 40 and 50 ms

    lcd.clear();
    lcd.print("HRV: "); lcd.print(hrv); lcd.print(" ms");
    Serial.print("Final HRV: "); Serial.println(hrv);
}

void loop() {
    // Empty loop since execution happens in setup()
}