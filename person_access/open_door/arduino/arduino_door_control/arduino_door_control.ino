
int door_pin = 8;
bool is_open = false;
long int now;

void setup() {
  pinMode(door_pin, OUTPUT);
  digitalWrite(door_pin, HIGH);
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    // read the incoming byte:
    int incomingByte = Serial.read();
//    Serial.println(incomingString);
    if(incomingByte=='o' and !is_open) {
      is_open = true;
    }
  }
  if(!is_open) {
    now=millis();
  }else{
    if(millis()-now<100){
      digitalWrite(door_pin, LOW);
    }else{
      digitalWrite(door_pin, HIGH);
      is_open=false;
    }
  }
}
