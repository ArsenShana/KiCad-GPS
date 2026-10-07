#include <deque>
#include <cstdint>
struct Point {uint64_t id; double lat,lon;};
static std::deque<Point> queue;
static uint64_t sequence=0, delivered=0, dropped=0;
static int route=0;
extern "C" {
void reset(){queue.clear();sequence=delivered=dropped=0;route=0;}
// ACK means durable server acceptance, including when relayed through phone.
// Unacknowledged head remains in queue with stable id for idempotent retries.
void step(int fix,double lat,double lon,int cell,int ble,int internet,int ack){
 if(fix){if(queue.size()<256) queue.push_back({++sequence,lat,lon});else ++dropped;}
 route=queue.empty()?0:(cell?1:((ble&&internet)?2:3));
 if((route==1||route==2)&&ack){queue.pop_front();++delivered;}
}
int pending(){return (int)queue.size();}
int channel(){return route;}
uint64_t sent(){return delivered;}
uint64_t lost(){return dropped;}
uint64_t head_id(){return queue.empty()?0:queue.front().id;}
double head_lat(){return queue.empty()?0:queue.front().lat;}
double head_lon(){return queue.empty()?0:queue.front().lon;}
}
