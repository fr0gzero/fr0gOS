// fr0gOS r30 crash / clip / perch / trick detector, run against simulated flights on the PC.
// make the include:  awk '/^\/\/ r29: crash, clip and perch from the physics/{p=1} /^static void frogFeedDetect/{p=0} p' src/main/osd/osd_elements.c > phys_core.inc
// then: gcc -O1 -o frog_physics_test frog_physics_test.c -lm && ./frog_physics_test
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define USE_ACC
#define USE_DSHOT_TELEMETRY
enum { X, Y, Z }; enum { FD_ROLL, FD_PITCH, FD_YAW };
typedef uint32_t timeUs_t; typedef int32_t timeDelta_t;
static timeDelta_t cmpTimeUs(timeUs_t a, timeUs_t b){return (timeDelta_t)(a-b);}
static float sq(float x){return x*x;}
static float constrainf(float v,float a,float b){return v<a?a:v>b?b:v;}
static struct { float gyroADCf[3]; } gyro;
static struct { struct { float v[3]; } accADC; struct { float acc_1G_rec; } dev; } acc = { .dev = { 1.0f } };
static float frogAccPeakG, frogThrustK, frogContactPeakG;
static int armed = 1; static float cosTilt = 1, SP[3], RPM = 0; static int THR = 0;
#define ARMING_FLAG(x) armed
static bool isCrashFlipModeActive(void){return false;}
static float getCosTiltAngle(void){return cosTilt;}
static int calculateThrottlePercent(void){return THR;}
static float getSetpointRate(int a){return SP[a];}
static int getMotorCount(void){return 4;}
static bool isDshotTelemetryActive(void){return true;}
static float getDshotRpm(uint8_t i){(void)i;return RPM;}
static float motor[4]; static float getMotorOutputLow(void){return 0;} static float getMotorOutputHigh(void){return 1;}
#define DEBUG_SET(a,b,c) do{}while(0)
#define FROG_TRICK_DEG       300.0f
#define FROG_TRICK_RATE      100.0f
#define FROG_TRICK_SLOW_MS   500
#define FROG_TRICK_MAX_MS    3000
static float RPMg, frogThrustProxyFilt;
static float frogThrustProxy(bool *rpm){*rpm=true; return sq(RPMg*1e-4f);}
#include "phys_core.inc"

// physics: true thrust scale, hover at 30000 rpm
static const float KTRUE = 1.0f / 9.0f;
static timeUs_t T = 1000000;
static void tick(float thr_pct, float rpm, float ax, float ay, float az_extra, float gx, float gy, float gz, float ctilt, float spike)
{
    THR = thr_pct; RPM = rpm; cosTilt = ctilt;
    const float thrust = KTRUE * sq(rpm * 1e-4f);
    acc.accADC.v[X] = ax; acc.accADC.v[Y] = ay; acc.accADC.v[Z] = thrust + az_extra;
    gyro.gyroADCf[0] = gx; gyro.gyroADCf[1] = gy; gyro.gyroADCf[2] = gz;
    const float mag = sqrtf(ax*ax + ay*ay + sq(thrust + az_extra));
    frogAccPeakG = MAX(mag, spike > 0 ? sqrtf(sq(spike) + sq(thrust)) : 0);
    RPMg = rpm; frogThrustProxyFilt = sq(rpm * 1e-4f);
    const float c = sqrtf(ax*ax + ay*ay + sq(thrust + az_extra - frogThrustK * sq(rpm * 1e-4f)));
    frogContactPeakG = MAX(c, spike);
    frogMotionTick(T);
    T += 10000;
}
static void report(const char *name, const char *expect)
{
    const char *n[] = {"ROLL","FLIP","SPIN","CRASH","PERCH","LOOP","CLIP"}; char out[80] = "";
    for (int i = 0; i < 7; i++) if (frogTrickPending & (1 << i)) { strcat(out, n[i]); strcat(out, " "); }
    printf("%-34s got [%s] expect [%s]\n", name, out, expect);
    frogTrickPending = 0;
}
static void sp(float a, float b, float c){SP[0]=a;SP[1]=b;SP[2]=c;}
static void hover(int ticks){ sp(0,0,0); for (int i=0;i<ticks;i++) tick(45, 30000, 0.05f*((i%7)-3)/3, 0.05f, 0, 5, -4, 3, 0.97f, 0); }
static void rearm(void){ armed=0; tick(0,0,0,0,1,0,0,0,1,0); frogTrickPending=0; armed=1; tick(0,0,0,0,1,0,0,0,1,0); frogTrickPending=0; }

int main(void)
{
    // takeoff + learn
    sp(0,0,0); for (int i=0;i<50;i++) tick(0, 4000, 0,0, 1.0f - KTRUE*0.16f, 0,0,0, 1, 0);
    hover(300); report("takeoff + hover 3 s", "");
    // cruise, wide turns, mild prop wash
    for (int i=0;i<500;i++){ sp(30*sinf(i*0.02f),20,60); tick(55, 33000, 0.3f, 0.2f, 0, 30*sinf(i*0.02f), 20, 60, 0.75f, 0);} report("cruise + wide turns 5 s", "");
    // low-throttle drop in midair (free fall-ish)
    sp(0,0,0); for (int i=0;i<150;i++) tick(10, 12000, 0,0, 0, 8,5,3, 0.98f, 0); report("throttle chop / dive 1.5 s midair", "");
    // slow descent at ~hover throttle
    for (int i=0;i<200;i++) tick(38, 28500, 0,0,0, 4,4,2, 0.99f, 0); report("slow descent", "");
    // big G turn / punch
    for (int i=0;i<80;i++) tick(100, 60000, 0.5f,0.3f,0, 50,40,20, 0.9f, 0); report("punch 4 G", "");
    hover(100);
    // flip: commanded 900 dps pitch 0.4 s, then stop with gyro lag
    sp(0,900,0); for (int i=0;i<42;i++) tick(30, 20000, 0,0,0, 0,900,0, 0.5f, 0);
    sp(0,0,0); for (int i=0;i<10;i++) tick(40, 30000, 0,0,0, 0,900-90*i,0, 0.9f, 0);
    hover(50); report("flip + snap stop", "FLIP");
    // roll at 1200 + abrupt stop
    sp(1200,0,0); for (int i=0;i<28;i++) tick(30, 20000, 0,0,0, 1200,0,0, 0.5f, 0);
    sp(0,0,0); for (int i=0;i<6;i++) tick(40, 30000, 0,0,0, 1200-200*i,0,0, 0.9f, 0);
    hover(50); report("roll + snap stop", "ROLL");
    // clip: 3.5 G touch, 400 dps jolt for 50 ms, flies on
    for (int i=0;i<5;i++) tick(50, 31000, 1.5f,0,0, 400,0,0, 0.95f, i==0?3.5f:0);
    hover(80); report("clip a branch, fly on", "CLIP");
    // soft perch: throttle down onto a branch
    for (int i=0;i<60;i++){ float r = 30000 - i*400; tick(45 - i*0.6f, r, 0,0, 0, 3,3,2, 0.99f, 0);} // thrust fades while the branch takes the weight
    for (int i=0;i<80;i++) tick(5, 6000, 0,0, 1.0f - KTRUE*0.36f, 2,2,1, 0.99f, 0);
    report("soft perch", "PERCH");
    // take off again
    for (int i=0;i<10;i++) tick(50, 31000, 0,0,0, 5,5,5, 0.98f, 0);
    hover(100); report("take off again", "");
    // firm landing: 3 G thump then rest upright idle
    tick(20, 15000, 0,0,0, 20,20,5, 0.98f, 3.0f);
    for (int i=0;i<60;i++) tick(5, 5000, 0,0, 1.0f - KTRUE*0.25f, 3,3,2, 0.99f, 0);
    report("firm landing", "PERCH");
    for (int i=0;i<10;i++) tick(50, 31000, 0,0,0, 5,5,5, 0.98f, 0); hover(100); report("take off again", "");
    // crash into a wall: 9 G, tumbles 1500 dps unasked for 0.3 s, lands upside down
    tick(60, 33000, 0,0,0, 300,0,0, 0.9f, 9.0f);
    for (int i=0;i<30;i++) tick(60, 20000, 0.5f,0.5f,0, 1500,800,300, 0.1f, 0);
    for (int i=0;i<60;i++) tick(5, 4000, 0,0, -1.0f - KTRUE*0.16f, 2,2,1, -0.98f, 0);
    report("wall crash, tumble, upside down", "CRASH");
    rearm(); hover(100); frogTrickPending=0;
    // crash: hits, drops upright on its side? lands on side, no tumble
    tick(50, 31000, 0,0,0, 50,0,0, 0.9f, 4.0f);
    for (int i=0;i<60;i++) tick(5, 4000, 1.0f,0, -KTRUE*0.16f, 2,2,1, 0.1f, 0);
    report("hit, ends on its side", "CRASH");
    rearm(); hover(100); frogTrickPending=0;
    // hard landing then disarm quickly while upright & still
    tick(20, 15000, 0,0,0, 20,20,5, 0.98f, 3.5f);
    for (int i=0;i<15;i++) tick(5, 5000, 0,0, 1.0f - KTRUE*0.25f, 3,3,2, 0.99f, 0);
    armed = 0; tick(0,0,0,0,1,0,0,0,0.99f,0); report("landing then quick disarm", "");
    armed = 1; tick(0,0,0,0,1,0,0,0,1,0); frogTrickPending=0;
    hover(100); frogTrickPending=0;
    // crashed into grass, props stuck, pilot disarms tilted
    tick(50, 31000, 0,0,0, 50,0,0, 0.9f, 5.0f);
    for (int i=0;i<20;i++) tick(30, 3000, 0.6f,0, 0.4f, 90,40,20, 0.4f, 0);
    armed = 0; tick(0,0,0,0,1,0,0,0,0.4f,0); report("stuck in grass, disarm", "CRASH");
    rearm(); hover(100); frogTrickPending=0;
    // knocked into a tumble midair (900 unasked for 0.4 s), recovers and flies on
    tick(50, 31000, 0,0,0, 900,300,0, 0.6f, 3.5f);
    for (int i=0;i<40;i++) tick(50, 31000, 0.3f,0.3f,0, 900,300,100, 0.3f, 0);
    hover(150); report("tumble midair, recovers", "CLIP");
    // fast forward flight with sloppy thrust model (0.8 G drag / error) for 4 s after a 3.2 G bump
    tick(70, 40000, 0,0,0, 50,0,0, 0.7f, 3.2f);
    for (int i=0;i<400;i++) tick(70, 40000, 0.8f,0,-0.5f, 60,30,20, 0.6f, 0);
    hover(100); report("bump then sloppy fast cruise", "");
    return 0;
}
