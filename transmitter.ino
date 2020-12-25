/*Arduino JOYSTICK CONTROLLED CAR (TRANSMITTER)
          
YOU HAVE TO INSTALL THE RF24 LIBRARY BEFORE UPLOADING THE CODE
   https://github.com/tmrh20/RF24/      
*/

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(8,9); // CE, CSN
const byte address[6] = "00001";
int py_val;
typedef struct{
  int in_val1;
  int in_val3;
  int speed_val;
  int delay_val_go;
  int delay_val_stop;
} send_vals;
send_vals sends;

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_MIN);
  radio.stopListening();
  sends.speed_val=127;
  sends.delay_val_go=20;
  sends.delay_val_stop=200;
}
void loop() {
  if(Serial.available()){
      py_val=Serial.read();
      if(py_val=='0'){
          sends.in_val1=0;
          sends.in_val3=1;
      }
    else if(py_val=='1'){
        sends.in_val1=1;
        sends.in_val3=0;
    }
    else if(py_val=='2'){
        sends.in_val1=1;
        sends.in_val3=1;
    }
    else{
      sends.in_val1=0;
      sends.in_val3=0;  
     }
  radio.write(&sends,sizeof(sends));    
  }
  else{
    sends.in_val1=-1;
   radio.write(&sends,sizeof(sends));
   delay(150);
   }
}
