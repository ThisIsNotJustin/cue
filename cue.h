#ifndef CUE_H
#define CUE_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

// https://developers.meethue.com/develop/application-design-guidance/color-conversion-formulas-rgb-to-xy-and-back/#Gamut
// Gamut C
#define RED_X 0.6915
#define RED_Y 0.3038
#define GREEN_X 0.17
#define GREEN_Y 0.7
#define BLUE_X 0.1532
#define BLUE_Y 0.0475
/*
// Gamut B
#define RED_X 0.675
#define RED_Y 0.322
#define GREEN_X 0.409
#define GREEN_Y 0.518
#define BLUE_X 0.167
#define BLUE__Y 0.04
// Gamut A
#define RED_X 0.704
#define RED_Y 0.296
#define GREEN_X 0.2151
#define GREEN_Y 0.7106
#define BLUE_X 0.138
#define BLUE__Y 0.08
// Alt
#define RED_X 1.0
#define RED_Y 0.0
#define GREEN_X 0.0
#define GREEN_Y 1.0
#define BLUE_X 0.0
#define BLUE__Y 0.0
*/

const char *MAC;
const char *POWER_UUID;
const char *BRIGHTNESS_UUID;
const char *TEMP_UUID;
const char *COLOR_UUID;

typedef struct {
    double x;
    double y;
    double brightness;
} XYPoint;

typedef struct {
    char *address;
    void *client;
} HueController;

bool within_gamut(XYPoint *point);
double euclidean_distance(XYPoint *a, XYPoint *b);
XYPoint point_to_segment(XYPoint *point, XYPoint *a, XYPoint *b);
XYPoint point_in_triangle(XYPoint *point);
XYPoint rgb_to_xy(size_t r, size_t g, size_t b);

HueController* controller_create(const char *address);
bool connect(HueController *controller);
void disconnect(HueController *controller);
bool power_on(HueController *controller);
bool power_off(HueController *controller);
bool set_brightness(HueController *controller, double brightness);
bool set_colors_xy(HueController *controller, double x, double y);
bool set_colors_rgb(HueController *controller, size_t r, size_t g, size_t b);

void discover_devices();

#endif // CUE_H