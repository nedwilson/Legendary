//
//  SMPTETimeCode.m
//  EDLParse
//
//  Created by Ned Wilson on 10/27/15.
//  Copyright © 2015 Ned Wilson. All rights reserved.
//

#import "SMPTETimeCode.h"

@implementation SMPTETimeCode

@synthesize hours = _hours;
@synthesize minutes = _minutes;
@synthesize seconds = _seconds;
@synthesize frames = _frames;

@synthesize fps = _fps;

@synthesize defaultFrameOneHour = _defaultFrameOneHour;

// initializers
-(id) initWithStringAndFPSAndDefault:(NSString *)stringTimeCode floatFPS:(float)fps defaultFOH:(int)foh {
    int thours, tminutes, tseconds, tframes;
    if (self = [super init]) {
        // Parse time code
        if ([stringTimeCode length] == 0) {
            NSException* wtf = [NSException exceptionWithName:@"ERROR:SMPTETimeCode.m"
                                                       reason:@"Zero-length TimeCode provided in initializer."
                                                     userInfo:nil];
            @throw wtf;
        }
        NSArray* tcarray = [stringTimeCode componentsSeparatedByString:@":"];
        if ([tcarray count] != 4) {
            NSException* wtf = [NSException exceptionWithName:@"ERROR:SMPTETimeCode.m"
                                                       reason:@"Incorrect TimeCode format provided in initializer.\nPlease use a string of the format 00:00:00:00."
                                                     userInfo:nil];
            @throw wtf;
        }
        thours = [[tcarray objectAtIndex:0] intValue];
        tminutes = [[tcarray objectAtIndex:1] intValue];
        tseconds = [[tcarray objectAtIndex:2] intValue];
        tframes = [[tcarray objectAtIndex:3] intValue];
        if (fps <= 0) {
            NSException* wtf = [NSException exceptionWithName:@"ERROR:SMPTETimeCode.m"
                                                       reason:[NSString stringWithFormat:@"FPS specified in initializer \"%f\" must be greater than zero.", fps]
                                                     userInfo:nil];
            @throw wtf;
        } else {
            _fps = fps;
        }
        if (foh < 0 || foh > 23) {
            NSException* wtf = [NSException exceptionWithName:@"ERROR:SMPTETimeCode.m"
                                                       reason:[NSString stringWithFormat:@"Frame One Hour specified in initializer \"%d\" must be between 0 and 23.", foh]
                                                     userInfo:nil];
            @throw wtf;
        } else {
            _defaultFrameOneHour = foh;
        }
        if (thours < 0 || thours > 23) {
            NSException* wtf = [NSException exceptionWithName:@"ERROR:SMPTETimeCode.m"
                                                       reason:[NSString stringWithFormat:@"Hours specified in TimeCode \"%d\" must be between 0 and 23.", thours]
                                                     userInfo:nil];
            @throw wtf;
        } else {
            _hours = thours;
        }
        if (tminutes < 0 || tminutes > 59) {
            NSException* wtf = [NSException exceptionWithName:@"ERROR:SMPTETimeCode.m"
                                                       reason:[NSString stringWithFormat:@"Minutes specified in TimeCode \"%d\" must be between 0 and 59.", tminutes]
                                                     userInfo:nil];
            @throw wtf;
        } else {
            _minutes = tminutes;
        }
        if (tseconds < 0 || tseconds > 59) {
            NSException* wtf = [NSException exceptionWithName:@"ERROR:SMPTETimeCode.m"
                                                       reason:[NSString stringWithFormat:@"Seconds specified in TimeCode \"%d\" must be between 0 and 59.", tseconds]
                                                     userInfo:nil];
            @throw wtf;
        } else {
            _seconds = tseconds;
        }
        if (tframes < 0 || tframes >= _fps) {
            NSException* wtf = [NSException exceptionWithName:@"ERROR:SMPTETimeCode.m"
                                                       reason:[NSString stringWithFormat:@"Frames specified in TimeCode \"%d\" must be between 0 and provided FPS %f.", tframes, _fps]
                                                     userInfo:nil];
            @throw wtf;
        } else {
            _frames = tframes;
        }
    } else {
        NSException* wtf = [NSException exceptionWithName:@"ERROR:SMPTETimeCode.m"
                                                   reason:@"Unable to initialize super class."
                                                 userInfo:nil];
        @throw wtf;
    }
    return self;
}
-(id) initWithStringAndFPS:(NSString *)stringTimeCode floatFPS:(float)fps {
    return [self initWithStringAndFPSAndDefault:stringTimeCode floatFPS:fps defaultFOH:0];
}
-(id) initWithString:(NSString *)stringTimeCode {
    return [self initWithStringAndFPSAndDefault:stringTimeCode floatFPS:24 defaultFOH:0];
}
-(id) init {
    return [self initWithStringAndFPSAndDefault:@"00:00:00:00" floatFPS:24 defaultFOH:0];
}

// class methods
-(NSString*) getTimeCode {
    return [NSString stringWithFormat:@"%02d:%02d:%02d:%02d", _hours, _minutes, _seconds, _frames];
}

-(int) timeCodeToFrame {
    int _tframe, _frame, _defaultFrameOne = 0;
    int _tfps = ceilf(_fps);
    _tframe = _frames + (_seconds*_tfps) + (_minutes*60*_tfps) + (_hours*3600*_tfps);
    _defaultFrameOne = (_defaultFrameOne*3600*_tfps);
    _frame = _tframe - _defaultFrameOne;
    return _frame + 1;
}

-(int) getDurationAsFrames:(SMPTETimeCode *)endTC {
    int _duration = 0;
    _duration = abs([self timeCodeToFrame] - [endTC timeCodeToFrame]) + 1;
    return _duration;
}

@end
