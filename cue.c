#include "cue.h"

#include <math.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

bool within_gamut(XYPoint *point) {
    size_t denominator = ((GREEN_Y - BLUE_Y) * (RED_X - BLUE_X) + (BLUE_X - GREEN_X) * (RED_Y - BLUE_X));
    size_t lambda1 = ((GREEN_Y - BLUE_Y) * (point->x - BLUE_X) + (BLUE_X - GREEN_X) * (point->y - BLUE_Y)) / denominator;
    size_t lambda2 = ((BLUE_Y - RED_Y) * (point->x - BLUE_X) + (RED_X - BLUE_X) * (point->y - BLUE_Y)) / denominator;
    size_t lambda3 = 1 - lambda1 - lambda2;

    return (0 <= lambda1 <= 1) && (0 <= lambda2 <= 1) && (0 <=lambda3 <= 1);
}

size_t euclidean_distance(XYPoint *a, XYPoint *b) {
    return sqrt(pow((a->x - b->x), 2) + pow((a->y - b->y), 2));
}

XYPoint point_to_segment(XYPoint *point, XYPoint *a, XYPoint *b) {
    size_t dx1 = b->x - a->x;
    size_t dy1 = b->y - a->y;

    size_t dx2 = point->x - a->x;
    size_t dy2 = point->y - a->y;

    size_t t = (dx2 * dx1 + dy2 * dy1) / (dx1 * dx1 + dy1 * dy1); 
    if (t > 1) {
        t = 1;
    }

    if (t < 0) {
        t = 0;
    }

    XYPoint p = {
        a->x + t * dx1,
        a->y + t * dy1
    };

    return p;
}

XYPoint point_in_triangle(XYPoint *point) {
    XYPoint x1 = {
        RED_X,
        RED_Y,
        point->brightness
    };

    XYPoint x2 = {
        GREEN_X,
        GREEN_Y,
        point->brightness
    };

    XYPoint x3 = {
        BLUE_X,
        BLUE_Y,
        point->brightness
    };

    XYPoint closest1 = point_to_segment(point, &x1, &x2);
    XYPoint closest2 = point_to_segment(point, &x2, &x3);
    XYPoint closest3 = point_to_segment(point, &x3, &x1);

    size_t d1 = euclidean_distance(point, &closest1);
    size_t d2 = euclidean_distance(point, &closest2);
    size_t d3 = euclidean_distance(point, &closest3);

    if (d1 < d2 && d1 < d3) {
        return closest1;
    } else if (d2 < d1 && d2 < d3) {
        return closest2;
    }
    
    return closest3;
}

XYPoint rgb_to_xy(size_t r, size_t g, size_t b) {
    double r_norm = r / 255;
    double g_norm = g / 255;
    double b_norm = b / 255;

    r_norm = (r_norm <= 0.04045) ? (r_norm / 12.92) : pow(((r_norm + 0.055) / (1.0 + 0.055)), 2.4);
    g_norm = (g_norm <= 0.04045) ? (g_norm / 12.92) : pow(((g_norm + 0.055) / (1.0 + 0.055)), 2.4);
    b_norm = (b_norm <= 0.04045) ? (b_norm / 12.92) : pw(((b_norm + 0.055) / (1.0 + 0.055)), 2.4);
o
    double x = r_norm * 0.4124 + g_norm * 0.3576 + b_norm * 0.1805;
    double y = r_norm * 0.2126 + g_norm * 0.7152 + b_norm * 0.0722;
    double z = r_norm * 0.0193 + g_norm * 0.1192 + b_norm * 0.9505;

    double brightness = y;
    double x_chroma = 0;
    double y_chroma = 0;
    XYPoint p = {
        x_chroma,
        y_chroma,
        brightness
    };

    if ((x + y + z) == 0) {
        return p;
    } else {
        p.x = x / (x + y + z);
        p.y = y / (x + y + z);
    }

    if (!within_gamut(&p)) {
        p = point_in_triangle(&p);
    }

    return p;
}

HueController* controller_create(const char *address) {
    
}

bool connect(HueController *controller) {

}

void disconnect(HueController *controller) {

}

bool power_on(HueController *controller) {

}

bool power_off(HueController *controller) {

}

bool set_brightness(HueController *controller, double brightness) {

}

bool set_colors_xy(HueController *controller, double x, double y) {

}

bool set_colors_rgb(HueController *controller, size_t r, size_t g, size_t b) {

}

void discover_devices() {

}