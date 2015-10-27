//
//  SMPTETimeCode.h
//  EDLParse
//
//  Created by Ned Wilson on 10/27/15.
//  Copyright © 2015 Ned Wilson. All rights reserved.
//

#import <Foundation/Foundation.h>
#include <math.h>

@interface SMPTETimeCode : NSObject

// Timecode hours
@property int hours;

// Timecode minutes
@property int minutes;

// Timecode seconds
@property int seconds;

// Timecode frames
@property int frames;

// Timecode FPS (default 24)
@property float fps;

// Timecode default frame one, i.e. 00:00:00:00 or 01:00:00:00
@property int defaultFrameOneHour;

// Initialize with a TimeCode string, i.e. 01:02:03:04
-(id) initWithString:(NSString*)stringTimeCode;

// Initialize with a TimeCode string and FPS, i.e. 24
-(id) initWithStringAndFPS:(NSString*)stringTimeCode floatFPS:(float)fps;

// Initialize with a TimeCode string, FPS, and default frame one hour, i.e. 0
-(id) initWithStringAndFPSAndDefault:(NSString*)stringTimeCode floatFPS:(float)fps defaultFOH:(int)foh;

// Returns the TimeCode as a formatted string
-(NSString*) getTimeCode;

// Converts the TimeCode to a frame number, based on the default frame one hour
-(int) timeCodeToFrame;

// Calculates the duration, in frames, between this SMPTETimeCode object and another
-(int) getDurationAsFrames:(SMPTETimeCode*)endTC;

@end
