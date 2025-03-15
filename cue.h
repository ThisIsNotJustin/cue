#ifndef CUE_H
#define CUE_H

#define RED_X 0.6915
#define RED_Y 0.3038
#define GREEN_X 0.17
#define GREEN_Y 0.7
#define BLUE_X 0.1532
#define BLUE__Y 0.0475

const char *MAC;
const char *POWER_UUID;
const char *BRIGHTNESS_UUID;
const char *TEMP_UUID;
const char *COLOR_UUID;

typedef struct {
    size_t x;
    size_t y;
    size_t brightness;
} XYPoint;

typedef struct {
    char *address;
    void *client;
} HueController;

bool within_gamut(XYPoint *point);
size_t euclidean_distance(XYPoint *a, XYPoint *b);
XYPoint point_to_segment(XYPoint *point, XYPoint *a, XYPoint *b);
XYPoint point_in_triangle(XYPoint *point);
XYPoint rgb_to_xy(size_t r, size_t g, size_t b);

HueController* controller_create(const char *address);
bool connect(HueController *controller);
void disconnect(HueController *controller);
bool power_on(HueController *controller);
bool power_off(HueController *controller);
bool set_brightness(HueController *controller, size_t brightness);
bool set_colors_xy(HueController *controller, size_t x, size_t y);
bool set_colors_rgb(HueController *controller, size_t r, size_t g, size_t b);

void discover_devices();

#endif // CUE_H