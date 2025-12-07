#include "Actuator.h"

ROVController::ROVController() {
    // Default pins
    PIN_1 = 1;   // Front
    PIN_2 = 15;  // Right
    PIN_3 = 2;   // Left
    PIN_4 = 16;  // Back
    PIN_5 = 39;  // Thruster
    
    // Default center positions
    CENTER_1 = 70;  // Front
    CENTER_2 = 71;  // Right
    CENTER_3 = 64;  // Left
    CENTER_4 = 73;  // Back
    
    // Initialize positions
    current1 = CENTER_1;
    current2 = CENTER_2;
    current3 = CENTER_3;
    current4 = CENTER_4;
    current5 = 0;
    
    target1 = CENTER_1;
    target2 = CENTER_2;
    target3 = CENTER_3;
    target4 = CENTER_4;
    target5 = 0;
}

void ROVController::setPins(int pin1, int pin2, int pin3, int pin4, int pin5) {
    PIN_1 = pin1;
    PIN_2 = pin2;
    PIN_3 = pin3;
    PIN_4 = pin4;
    PIN_5 = pin5;
}

void ROVController::setCenterPositions(int c1, int c2, int c3, int c4) {
    CENTER_1 = c1;
    CENTER_2 = c2;
    CENTER_3 = c3;
    CENTER_4 = c4;
    
    current1 = target1 = CENTER_1;
    current2 = target2 = CENTER_2;
    current3 = target3 = CENTER_3;
    current4 = target4 = CENTER_4;
}

void ROVController::begin() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("=== ROV Controller Starting ===");
    
    // Setup Servos 1-4
    Serial.println("Setting up Servo 1 (Front)...");
    servo1.setPeriodHertz(50);
    servo1.attach(PIN_1, 500, 2500);
    servo1.write(CENTER_1);
    delay(100);
    
    Serial.println("Setting up Servo 2 (Right)...");
    servo2.setPeriodHertz(50);
    servo2.attach(PIN_2, 500, 2500);
    servo2.write(CENTER_2);
    delay(100);
    
    Serial.println("Setting up Servo 3 (Left)...");
    servo3.setPeriodHertz(50);
    servo3.attach(PIN_3, 500, 2500);
    servo3.write(CENTER_3);
    delay(100);
    
    Serial.println("Setting up Servo 4 (Back)...");
    servo4.setPeriodHertz(50);
    servo4.attach(PIN_4, 500, 2500);
    servo4.write(CENTER_4);
    delay(100);
    
    Serial.println("Servos 1-4 ready!");
    
    // Setup Thruster
    Serial.println("⚠️  Setting up Thruster ESC...");
    servo5.setPeriodHertz(50);
    servo5.attach(PIN_5, 1000, 2000);
    delay(100);
    
    Serial.println("Arming ESC...");
    servo5.writeMicroseconds(1000);
    delay(3000);
    Serial.println("✅ Thruster Ready!");
    
    Serial.println("\n=== ROV Controller Ready ===");
    Serial.println("Center positions:");
    Serial.println("  1-Front:    " + String(CENTER_1) + "° (±10)");
    Serial.println("  2-Right:    " + String(CENTER_2) + "° (±10)");
    Serial.println("  3-Left:     " + String(CENTER_3) + "° (±10)");
    Serial.println("  4-Back:     " + String(CENTER_4) + "° (±10)");
    Serial.println("  5-Thruster: 0 (0-100)");
    Serial.println("\nCommands:");
    Serial.println("  center           → servos 1-4 to center");
    Serial.println("  1 <-10~10>       → servo 1 offset");
    Serial.println("  2 <-10~10>       → servo 2 offset");
    Serial.println("  3 <-10~10>       → servo 3 offset");
    Serial.println("  4 <-10~10>       → servo 4 offset");
    Serial.println("  5 <0~100>        → thruster power");
    Serial.println("  all <-10~10>     → all servos 1-4 same offset");
    Serial.println("  set <1> <2> <3> <4> → set all offsets");
    Serial.println("  stop             → thruster to 0");
    Serial.println("  status           → show current positions");
    Serial.println();
}

void ROVController::update() {
    processSerialCommand();
    updateServos();
    delayMicroseconds(800);
}

void ROVController::processSerialCommand() {
    if (!Serial.available()) return;
    
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd.length() == 0) return;
    
    Serial.print("[DEBUG] Received: '");
    Serial.print(cmd);
    Serial.println("'");
    
    String cmdLower = cmd;
    cmdLower.toLowerCase();
    
    if (cmdLower == "center") {
        moveToCenter();
        Serial.println("→ Servos 1-4 to center");
        
    } else if (cmdLower == "stop") {
        stop();
        
    } else if (cmdLower == "status") {
        showStatus();
        
    } else if (cmd.startsWith("1 ") || cmd.startsWith("1\t")) {
        int offset = cmd.substring(2).toInt();
        setServo(1, offset);
        
    } else if (cmd.startsWith("2 ") || cmd.startsWith("2\t")) {
        int offset = cmd.substring(2).toInt();
        setServo(2, offset);
        
    } else if (cmd.startsWith("3 ") || cmd.startsWith("3\t")) {
        int offset = cmd.substring(2).toInt();
        setServo(3, offset);
        
    } else if (cmd.startsWith("4 ") || cmd.startsWith("4\t")) {
        int offset = cmd.substring(2).toInt();
        setServo(4, offset);
        
    } else if (cmd.startsWith("5 ") || cmd.startsWith("5\t")) {
        int power = cmd.substring(2).toInt();
        setThruster(power);
        
    } else if (cmdLower.startsWith("all ")) {
        int offset = cmd.substring(4).toInt();
        setAllServos(offset);
        
    } else if (cmdLower.startsWith("set ")) {
        parseSetCommand(cmd);
        
    } else {
        Serial.println("❌ Unknown command: '" + cmd + "'");
    }
    
    while(Serial.available()) Serial.read();
}

void ROVController::moveToCenter() {
    target1 = CENTER_1;
    target2 = CENTER_2;
    target3 = CENTER_3;
    target4 = CENTER_4;
}

void ROVController::setServo(int servoNum, int offset) {
    offset = constrain(offset, -RANGE, RANGE);
    
    switch(servoNum) {
        case 1:
            target1 = CENTER_1 + offset;
            Serial.print("→ Servo 1 (Front): ");
            Serial.print(CENTER_1);
            Serial.print(offset >= 0 ? "+" : "");
            Serial.print(offset);
            Serial.print(" = ");
            Serial.print(target1);
            Serial.println("°");
            break;
            
        case 2:
            target2 = CENTER_2 + offset;
            Serial.print("→ Servo 2 (Right): ");
            Serial.print(CENTER_2);
            Serial.print(offset >= 0 ? "+" : "");
            Serial.print(offset);
            Serial.print(" = ");
            Serial.print(target2);
            Serial.println("°");
            break;
            
        case 3:
            target3 = CENTER_3 + offset;
            Serial.print("→ Servo 3 (Left): ");
            Serial.print(CENTER_3);
            Serial.print(offset >= 0 ? "+" : "");
            Serial.print(offset);
            Serial.print(" = ");
            Serial.print(target3);
            Serial.println("°");
            break;
            
        case 4:
            target4 = CENTER_4 + offset;
            Serial.print("→ Servo 4 (Back): ");
            Serial.print(CENTER_4);
            Serial.print(offset >= 0 ? "+" : "");
            Serial.print(offset);
            Serial.print(" = ");
            Serial.print(target4);
            Serial.println("°");
            break;
    }
}

void ROVController::setThruster(int power) {
    power = constrain(power, THRUSTER_MIN, THRUSTER_MAX);
    target5 = power;
    
    int pwmVal = map(power, 0, 100, 1000, 2000);
    
    Serial.print("→ Thruster: ");
    Serial.print(power);
    Serial.print("% (");
    Serial.print(pwmVal);
    Serial.println("us)");
}

void ROVController::setAllServos(int offset) {
    offset = constrain(offset, -RANGE, RANGE);
    
    target1 = CENTER_1 + offset;
    target2 = CENTER_2 + offset;
    target3 = CENTER_3 + offset;
    target4 = CENTER_4 + offset;
    
    Serial.print("→ All servos offset: ");
    Serial.print(offset);
    Serial.println("°");
    Serial.print("  1:");
    Serial.print(target1);
    Serial.print("° 2:");
    Serial.print(target2);
    Serial.print("° 3:");
    Serial.print(target3);
    Serial.print("° 4:");
    Serial.print(target4);
    Serial.println("°");
}

void ROVController::stop() {
    target5 = 0;
    Serial.println("→ Thruster STOP");
}

void ROVController::parseSetCommand(String cmd) {
    int offsets[4] = {0, 0, 0, 0};
    int count = 0;
    
    int startPos = 4;
    for (int i = 0; i < 4; i++) {
        int spacePos = cmd.indexOf(' ', startPos);
        if (spacePos == -1 && i < 3) break;
        
        String numStr;
        if (spacePos == -1) {
            numStr = cmd.substring(startPos);
        } else {
            numStr = cmd.substring(startPos, spacePos);
        }
        
        offsets[i] = constrain(numStr.toInt(), -RANGE, RANGE);
        count++;
        startPos = spacePos + 1;
    }
    
    if (count == 4) {
        target1 = CENTER_1 + offsets[0];
        target2 = CENTER_2 + offsets[1];
        target3 = CENTER_3 + offsets[2];
        target4 = CENTER_4 + offsets[3];
        
        Serial.println("→ Set all servos:");
        Serial.print("  1(Front): ");
        Serial.print(CENTER_1);
        Serial.print(offsets[0] >= 0 ? "+" : "");
        Serial.print(offsets[0]);
        Serial.print(" = ");
        Serial.print(target1);
        Serial.println("°");
        
        Serial.print("  2(Right): ");
        Serial.print(CENTER_2);
        Serial.print(offsets[1] >= 0 ? "+" : "");
        Serial.print(offsets[1]);
        Serial.print(" = ");
        Serial.print(target2);
        Serial.println("°");
        
        Serial.print("  3(Left):  ");
        Serial.print(CENTER_3);
        Serial.print(offsets[2] >= 0 ? "+" : "");
        Serial.print(offsets[2]);
        Serial.print(" = ");
        Serial.print(target3);
        Serial.println("°");
        
        Serial.print("  4(Back):  ");
        Serial.print(CENTER_4);
        Serial.print(offsets[3] >= 0 ? "+" : "");
        Serial.print(offsets[3]);
        Serial.print(" = ");
        Serial.print(target4);
        Serial.println("°");
    } else {
        Serial.println("❌ Format: set <off1> <off2> <off3> <off4>");
        Serial.println("   Example: set 2 -3 0 5");
    }
}

void ROVController::updateServos() {
    int step = 1;
    int thrustStep = 2;
    
    // Servo 1-4
    if (current1 != target1) {
        current1 += (current1 < target1) ? step : -step;
        servo1.write(current1);
    }
    
    if (current2 != target2) {
        current2 += (current2 < target2) ? step : -step;
        servo2.write(current2);
    }
    
    if (current3 != target3) {
        current3 += (current3 < target3) ? step : -step;
        servo3.write(current3);
    }
    
    if (current4 != target4) {
        current4 += (current4 < target4) ? step : -step;
        servo4.write(current4);
    }
    
    // Thruster
    if (current5 != target5) {
        int diff = target5 - current5;
        if (abs(diff) > thrustStep) {
            current5 += (current5 < target5) ? thrustStep : -thrustStep;
        } else {
            current5 = target5;
        }
        
        int pwmVal = map(current5, 0, 100, 1000, 2000);
        servo5.writeMicroseconds(pwmVal);
    }
}

void ROVController::showStatus() {
    Serial.println("\n=== Current Status ===");
    
    Serial.print("Servo 1 (Front): ");
    Serial.print(current1);
    Serial.print("° (");
    Serial.print(CENTER_1);
    Serial.print(current1 - CENTER_1 >= 0 ? "+" : "");
    Serial.print(current1 - CENTER_1);
    Serial.println("°)");
    
    Serial.print("Servo 2 (Right): ");
    Serial.print(current2);
    Serial.print("° (");
    Serial.print(CENTER_2);
    Serial.print(current2 - CENTER_2 >= 0 ? "+" : "");
    Serial.print(current2 - CENTER_2);
    Serial.println("°)");
    
    Serial.print("Servo 3 (Left):  ");
    Serial.print(current3);
    Serial.print("° (");
    Serial.print(CENTER_3);
    Serial.print(current3 - CENTER_3 >= 0 ? "+" : "");
    Serial.print(current3 - CENTER_3);
    Serial.println("°)");
    
    Serial.print("Servo 4 (Back):  ");
    Serial.print(current4);
    Serial.print("° (");
    Serial.print(CENTER_4);
    Serial.print(current4 - CENTER_4 >= 0 ? "+" : "");
    Serial.print(current4 - CENTER_4);
    Serial.println("°)");
    
    Serial.print("Thruster:        ");
    Serial.print(current5);
    Serial.println("%");
    Serial.println();
}

int ROVController::getCurrentServo(int servoNum) {
    switch(servoNum) {
        case 1: return current1;
        case 2: return current2;
        case 3: return current3;
        case 4: return current4;
        default: return 0;
    }
}

int ROVController::getCurrentThruster() {
    return current5;
}