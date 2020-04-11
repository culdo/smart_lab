/* 
[credit]
http://wyj-learning.blogspot.com/2017/12/arduino-06.html
 */

const int IR_rec_pin = 11;             // IR 接收器輸出腳位
int IRstate = LOW;                    // IR 接收器輸出腳位狀態
int IRstate_last = LOW;               // IR 接收器輸出腳位狀態(上一次)
unsigned long int time_last = 0;      // 上一次 IRstate 變化的時間
boolean isIdle = true;                // 是否在等待 IR 訊號模式Idle）
const long int durationMax = 10000;   // 一段時間沒變化就進入 Idle，單位 us
const long int durationMin = 300;     // 電壓狀態不變的最小持續時間，單位 us

void IR_rec_Check();

void setup( ) {
  Serial.begin( 115200 );
  pinMode( IR_rec_pin, INPUT );        // 設定針腳 I/O 模式
  IRstate = digitalRead( IR_rec_pin ); // 取得腳位元狀態初始值
  IRstate_last = IRstate;
}
void loop( ) {
  IR_rec_Check();
  delayMicroseconds( 5 );
}

void IR_rec_Check(){
  
  IRstate = digitalRead( IR_rec_pin );// 讀取腳位狀態

  if( IRstate != IRstate_last ){      //

    long int timeNow = micros( );      // 記錄目前時間
    long int dT = timeNow - time_last; // 與上一次腳位變化的時間差

      if( (dT >= durationMax) && !isIdle ){     // 時間間隔大於設定的時間，且原本的狀態為接收中狀態
        isIdle = true; //進入等待狀態
        Serial.println( "Idling...\n" );
      }
      else if( (dT < durationMax) && (dT > durationMin) ){
        isIdle = false; //進入接收中狀態
          if(IRstate == HIGH) Serial.print(dT);
          else  Serial.print( 0-dT );
        Serial.print(", ");
      }
 // 記錄此次時間
  time_last = timeNow;
  }
 // 記錄此次狀態
 IRstate_last = IRstate;
}//end IR_rec_Check
