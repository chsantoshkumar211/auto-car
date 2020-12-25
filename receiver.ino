/*ARDUINO JOYSTICK CONTROLLED CAR (RECEIVER)
        
YOU HAVE TO INSTALL THE RF24 LIBRARY BEFORE UPLOADING THE CODE
   https://github.com/tmrh20/RF24/        
*/
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#define enA 2  
#define in1 3
#define in2 4
#define enB 7   
#define in3 5
#define in4 6
RF24 radio(8,9); // CE, CSN
const byte address[6] = "00001";
typedef struct 
{
    int in_val1;
    int in_val3;
    int speed_val;
    int delay_val_go;
    int delay_val_stop;
}send_vals;
send_vals sends;
void setup() {
  pinMode(enA, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  digitalWrite(in2,LOW);
  digitalWrite(in4,LOW);
  Serial.begin(9600);
  radio.begin();
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();
}
void loop() {
    if(radio.available()){
        radio.read(&sends,sizeof(sends));
        Serial.println(sends.in_val1);
        if(sends.in_val1==1) digitalWrite(in1,HIGH);
        else digitalWrite(in1,LOW);
        if(sends.in_val3==1) digitalWrite(in3,HIGH);
        else digitalWrite(in3,LOW);
         if(sends.in_val1==-1){
         digitalWrite(in1,LOW);
         digitalWrite(in3,LOW);
         analogWrite(enA,0);
         analogWrite(enB,0); 
         }
         else{
          analogWrite(enA,sends.speed_val);
          analogWrite(enB,sends.speed_val);
          delay(sends.delay_val_go);
          analogWrite(enA,0);
          analogWrite(enB,0);
          delay(sends.delay_val_stop);
         }
    }
}
