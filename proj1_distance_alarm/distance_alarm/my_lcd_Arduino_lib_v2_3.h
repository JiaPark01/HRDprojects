#include "Arduino.h"

// V1.0 = 1995, 5, 18 = 최초작성
// V2.0 = 2023, 1, 10 = ARM Corte-Mx용 으로 수정
// V2.2 = 2023, 1, 11 = User Font R/W Func 추가
// V2.3 = 2023, 3, 20 = Arduino 버전으로 수정
// Song Myoung Gyu


#ifndef __my_lcd_lib__
#define __my_lcd_lib__

//---------------------------------
// hw pin map == 프로세서에 따라 수정
#define MCU_RS_PIN  8       // arduino D8
#define MCU_EN_PIN  9       // arduino D9

#define lcd_rs   MCU_RS_PIN
#define lcd_rw   0          // NC = GND
#define lcd_en   MCU_EN_PIN

#define en_ck  (d_out(lcd_en, 1), delayMicroseconds(1), d_out(lcd_en, 0), delayMicroseconds(100)) // 6 pin

//---------------------------------
// lcd Control Command
#define        LCD_CLR           (lcd_cmd(0x01))  // lcd clear
 
   // display move ==>> rr / ll (up to 16 times)
#define        L_MV              (lcd_cmd(0x18))
#define        R_MV              (lcd_cmd(0x1c))

   // curser move ==>> rr / ll
#define        CUR_R_MV          (lcd_cmd(0x14))
#define        CUR_L_MV          (lcd_cmd(0x10))

   // entry move ==>> rr / ll
#define        ENTRY_STOP        (lcd_cmd(0x05))
#define        E_L_MV            (lcd_cmd(0x07))
#define        E_R_MV            (lcd_cmd(0x06))  // default == auto rr move

   // curser 
#define        CUR_HOME          (lcd_cmd(0x02))
#define        CUR_ON            (lcd_cmd(0x0f))
#define        CUR_OFF           (lcd_cmd(0x0c))  //0x0d

   // display
#define        DIS_ON            (lcd_cmd(0x0c)) // display all on, curser off
#define        DIS_OFF           (lcd_cmd(0x0b))  

// line home
#define        DIS_1_HOME        (lcd_cmd(0x80))  // (0, 0)
#define        DIS_2_HOME        (lcd_cmd(0xc0))  // (0, 1)
#define        DIS_3_HOME        (lcd_cmd(0x94))  // hardware not supported
#define        DIS_4_HOME        (lcd_cmd(0xd4))

#ifdef LCD_IF_4_Bit
  #define        FUNC_SET_4BIT     (lcd_cmd(0x28))
  #define        bit_4_if          (lcd_cmd(0x28)) // 2018, 5, 12 �߰�
#elif LCD_IF_8_Bit
  #define        FUNC_SET_8BIT     (lcd_cmd(0x38))
  #define        bit_8_if          (lcd_cmd(0x38)) // 2018, 5, 12 추가
#elif LCD_IF_I2C
  // Nest Ver
#endif

#ifdef LCD_PA
  #define LCD_PORT GPIOA
#elif LCD_PB
  #define LCD_PORT GPIOB
#elif LCD_PC
  #define LCD_PORT GPIOC
#elif LCD_PD    // 2023, 3, 20 추가
  #define LCD_PORT PORTD
// #elif Arduino   // 2023, 3, 20 추가
//   #define LCD_PORT(data) d_out(data)
#endif

#define lcd_out(val) (LCD_PORT = val)   // 8bit


void lcd_cmd(unsigned char com)
{
  // lcd control command wr func
	d_out(lcd_rs, 0); // rs, rw, en = 0

#ifdef LCD_IF_8_Bit
  // 8bit
  lcd_out(com); // 8bit 
  en_ck;
#elif LCD_IF_4_Bit
  // 4bit
  lcd_out(com & 0xf0); // hi 4bit out
  en_ck;
  lcd_out(com  << 4); // low 4bit out
  en_ck;
#endif
} 

void lcd_gotoxy(char x, char y)
{
  // lcd display 표시 좌표 설정 
  if(y == 1) lcd_cmd(x + 0x80); // 1 line
  else if(y == 2) lcd_cmd(x + 0xc0); // 2 line 
  else if(y == 3) lcd_cmd(x + 0x94); // 2 line
  else if(y == 4) lcd_cmd(x + 0xd4); // 2 line     
}

// 한 문자 출력
void lcd_send(unsigned char buf)
{
  // user data display
	d_out(lcd_rs, 1); // User data display rs = 1;
  
#ifdef LCD_IF_8_Bit
  // 8bit
  lcd_out(buf); // 8bit
  en_ck;
#elif  LCD_IF_4_Bit
  // 4bit
  lcd_out(buf & 0xf0); // hi 4bit out
  en_ck;
  lcd_out(buf  << 4); // low 4bit out
  en_ck;
#endif
}

// 문자열 출력
// 2023, 3, 20 수정
void lcd_str(unsigned char *buf)
{
  // user string data display 
  while(*buf != '\0')
   {
     lcd_send(*buf);
     buf++;
   }
}

// 여러 data 출력할 수 있음
// 2023, 3, 20 수정
void lcd_data(unsigned char *buf)
{
  // user string data display 
  while(*buf != '\n')
   {
     lcd_send(*buf);
     buf++;
   }
}  

void lcd_gotoxy_str(char x, char y, unsigned char *buf)
{
 // 좌표 설정 후 바로 문자열 출력
 lcd_gotoxy(x,y);
 lcd_str(buf);
}

// LCD 초기화 함수
void lcd_init()
{
  // cld �ʱ�ȭ
  d_out(lcd_rs, 0);   // 
  d_out(lcd_en, 0);  // lcd_rw = gpio pin control �Ҷ��� �ʱ�ȭ �ϼ���
  lcd_out(0x00);

#ifdef LCD_IF_8_Bit
  FUNC_SET_8BIT; // lcd_out(0x38); // 8bit if  = 4bit = 0x28;
#elif  LCD_IF_4_Bit
  FUNC_SET_4BIT; // 0x28
#endif

 delay(100);
#ifdef LCD_IF_8_Bit
  FUNC_SET_8BIT; // lcd_out(0x38); // 8bit if  = 4bit = 0x28;
#elif  LCD_IF_4_Bit
  FUNC_SET_4BIT; // 0x28
#endif
  delay(100);

#ifdef LCD_IF_8_Bit
  FUNC_SET_8BIT; // lcd_out(0x38); // 8bit if  = 4bit = 0x28;
#elif  LCD_IF_4_Bit
  FUNC_SET_4BIT; // 0x28
#endif
  delay(100);

  // entry mode set
  E_R_MV;   //lcd_out(0x06); //default 06
  delay(30);

  // lcd clr
 LCD_CLR;
 delay(30);

 // lcd display on
 DIS_ON;  //0c
 delay(30);

 // curser home  0,0
 CUR_HOME; //lcd_out(0x02);
 delay(30);
}

void bit_4_out(char data)
{
	char buf;

	buf = data & 0xf0;
	lcd_send(buf);
	en_ck;

	buf = data & 0x0f;
	buf <<= 4;
	lcd_send(buf);
	en_ck;
}

//===========================================================

// lcd user font display

//cg ram address = 0x40 - 0x7f (0x80 - 0xff)
//  i = 0 = 0x40 // User start Adderss = Index = 0(read)
//  i = 1 = 0x48                       = Index = 1(read)
//  i = 2 = 0x50
//  i = 3 = 0x58
//  i = 4 = 0x60
//  i = 5 = 0x68
//  i = 6 = 0x70
//  i = 7 = 0x78                       = Index = 7(read)
//
//  5x8(7) = 8자
//  5x10 = 4자

// lcd user font display
#ifdef Char_LCD_User_Font

// cg ram start address
#define st_adr_1    0x40
#define st_adr_2    0x48
#define st_adr_3    0x50
#define st_adr_4    0x58
#define st_adr_5    0x60
#define st_adr_6    0x68
#define st_adr_7    0x70
#define st_adr_8    0x78

#ifdef User_Font_Sample
  #include  "User_Font_Sample.h"
#endif

 char user_font_1[8]; // user font Arry
 char user_font_2[8][8];  // user font Arry

void fount_wr_8(char dis)
{
  // 8자 User Font Data를 한번에 다 Write 할 경우에만 사용
  int i;

// User Font WR Func
if(dis == 1)
 { // 비반전 = default
   for(i=0; i < 7; i++)
    {
     lcd_cmd(0x40+i); lcd_send(user_font_2[0][i]); delay(1);
     lcd_cmd(0x48+i); lcd_send(user_font_2[1][i]); delay(1);
     lcd_cmd(0x50+i); lcd_send(user_font_2[2][i]); delay(1);
     lcd_cmd(0x58+i); lcd_send(user_font_2[3][i]); delay(1);
     lcd_cmd(0x60+i); lcd_send(user_font_2[4][i]); delay(1);
     lcd_cmd(0x68+i); lcd_send(user_font_2[5][i]); delay(1);
     lcd_cmd(0x70+i); lcd_send(user_font_2[6][i]); delay(1);
     lcd_cmd(0x78+i); lcd_send(user_font_2[7][i]); delay(1);
    }
  }
 else
  {
	// 반전 = 0
	 for(i=0; i < 7; i++)
	     {
	      lcd_cmd(0x40+i); lcd_send(~user_font_2[0][i]); delay(1);
	      lcd_cmd(0x48+i); lcd_send(~user_font_2[1][i]); delay(1);
	      lcd_cmd(0x50+i); lcd_send(~user_font_2[2][i]); delay(1);
	      lcd_cmd(0x58+i); lcd_send(~user_font_2[3][i]); delay(1);
	      lcd_cmd(0x60+i); lcd_send(~user_font_2[4][i]); delay(1);
	      lcd_cmd(0x68+i); lcd_send(~user_font_2[5][i]); delay(1);
	      lcd_cmd(0x70+i); lcd_send(~user_font_2[6][i]); delay(1);
	      lcd_cmd(0x78+i); lcd_send(~user_font_2[7][i]); delay(1);
	     }
  }
}

void user_font_wr(char st_adr, char max_adr, char dis)
{
  // User Font Data를 설정한대로 만 쓰는거 = 최대 8개
  char i, j, k = 0;

  for( i = 0; i <= max_adr; i++) // max 7
    {
     lcd_cmd(st_adr + (i<<3));

     for( j = 0; j <= 7; j++)
      {
       if(dis == 0) lcd_send(~user_font_2[i][j]); // 반전 = 0
       else	lcd_send(user_font_2[i][j]);          // 비반전 = 1
      }
   }
}

void user_font_wr_1(char st_adr, char dis)
{
  // 1개의 1차원 배열 User Font을 하나의 어드레스에 쓸경우 사용
  char k;
  for(k=0; k< 8; k++)
   {
     lcd_cmd(st_adr + k);
     if(dis == 0) lcd_send(~user_font_1[k]);
     else lcd_send(user_font_1[k]);
   }
}
//--------------------------------------------------

// User Font Read Func
void user_font_rd_8()
 {
  // 먼저 쓰고 그다음 읽기
   lcd_send(0x00);  // 0x40 = ST_ADR 1  == 0
   lcd_send(0x01);  // 0x48 = ST_ADR 2  == 1
   lcd_send(0x02);  //                  == 2 ...
   lcd_send(0x03);
   lcd_send(0x04);
   lcd_send(0x05);
   lcd_send(0x06);
   lcd_send(0x07); // 0x78 = = ST_ADR 8 == 7
}

void user_font_rd_1(char st_adr)
{
 lcd_send(st_adr);
}
#endif

#endif
