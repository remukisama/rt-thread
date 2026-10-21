typedef unsigned long u64;
typedef long s64;
static inline s64 call(u64 n,u64 a,u64 b,u64 c,u64 d,u64 e,u64 f)
{
 register u64 x8 __asm__("x8")=n;
 register u64 x0 __asm__("x0")=a;
 register u64 x1 __asm__("x1")=b;
 register u64 x2 __asm__("x2")=c;
 register u64 x3 __asm__("x3")=d;
 register u64 x4 __asm__("x4")=e;
 register u64 x5 __asm__("x5")=f;
 __asm__ volatile("svc #0":"+r"(x0):"r"(x8),"r"(x1),"r"(x2),"r"(x3),"r"(x4),"r"(x5):"memory","cc");
 return (s64)x0;
}
static void log(const char *s){int n=0;while(s[n])n++;call(255,(u64)s,n,0,0,0,0);}
static void exit_test(int error){log(error?"[USER] FAIL\n":"[USER] PASS\n");call(1,error,0,0,0,0,0);for(;;);}
void _start(void)
{
 static const char path[]="/user_tmp/data";
 static const char content[]="0123456789abcdef";
 char buffer[32];
 if(call(176,(u64)"tmp",(u64)"/user_tmp",(u64)"tmp",0,0,0)!=0)exit_test(1);
 s64 fd=call(5,(u64)path,2|64,0600,0,0,0);
 if(fd<0)exit_test(2);
 if(call(3,fd,(u64)content,16,0,0,0)!=16)exit_test(3);
 if(call(201,fd,4096,0,0,0,0)!=0)exit_test(4);
 if(call(201,fd,0,0,0,0,0)!=0)exit_test(5);
 if(call(4,fd,0,0,0,0,0)!=0)exit_test(6);
 if(call(2,fd,(u64)buffer,sizeof(buffer),0,0,0)!=0)exit_test(7);
 if(call(3,fd,(u64)content,16,0,0,0)!=16)exit_test(8);
 if(call(4,fd,0,0,0,0,0)!=0)exit_test(9);
 if(call(2,fd,(u64)buffer,16,0,0,0)!=16)exit_test(10);
 for(int i=0;i<16;i++)if(buffer[i]!=content[i])exit_test(11);
 if(call(6,fd,0,0,0,0,0)!=0)exit_test(12);
 if(call(118,(u64)path,0,0,0,0,0)!=0)exit_test(13);
 exit_test(0);
}
