//
//  EDLEvent.m
//  EDLParse
//
//  Created by Ned Wilson on 10/27/15.
//  Copyright © 2015 Ned Wilson. All rights reserved.
//

#import "EDLEvent.h"

@implementation EDLEvent

@synthesize eventNumber;
@synthesize clipIn;
@synthesize clipOut;
@synthesize recIn;
@synthesize recOut;
@synthesize reelName;
@synthesize trackType;
@synthesize editType;
@synthesize slopeR;
@synthesize slopeG;
@synthesize slopeB;
@synthesize offsetR;
@synthesize offsetG;
@synthesize offsetB;
@synthesize powerR;
@synthesize powerG;
@synthesize powerB;
@synthesize saturation;

@synthesize frameIn;
@synthesize frameOut;
@synthesize frameCount;
@synthesize comments;

@dynamic clipInStr;
@dynamic clipOutStr;
@dynamic recInStr;
@dynamic recOutStr;

-(id) initWithRecord:(int)mEventNumber dClipIn:(SMPTETimeCode*)mClipIn dClipOut:(SMPTETimeCode*)mClipOut dRecIn:(SMPTETimeCode*)mRecIn dRecOut:(SMPTETimeCode*)mRecOut dReelName:(NSString*)mReelName dTrackType:(NSString*)mTrackType dEditType:(NSString*)mEditType dSlopeR:(float)mSlopeR dSlopeG:(float)mSlopeG dSlopeB:(float)mSlopeB dOffsetR:(float)mOffsetR dOffsetG:(float)mOffsetG dOffsetB:(float)mOffsetB dPowerR:(float)mPowerR dPowerG:(float)mPowerG dPowerB:(float)mPowerB dSaturation:(float)mSaturation {
    if (self = [super init]) {
        eventNumber = mEventNumber;
        clipIn = mClipIn;
        clipOut = mClipOut;
        recIn = mRecIn;
        recOut = mRecOut;
        reelName = mReelName;
        trackType = mTrackType;
        editType = mEditType;
        slopeR = mSlopeR;
        slopeG = mSlopeG;
        slopeB = mSlopeB;
        offsetR = mOffsetR;
        offsetG = mOffsetG;
        offsetB = mOffsetB;
        powerR = mPowerR;
        powerG = mPowerG;
        powerB = mPowerB;
        saturation = mSaturation;
        
        frameIn = [clipIn timeCodeToFrame];
        frameOut = [clipOut timeCodeToFrame];
        frameCount = [clipIn getDurationAsFrames:clipOut];
    } else {
        NSException* wtf = [NSException exceptionWithName:@"ERROR:EDLEvent.m"
                                                   reason:@"Unable to initialize super class."
                                                 userInfo:nil];
        @throw wtf;
    }
    return self;
}
-(id) init {
    return [self initWithRecord:0 dClipIn:[[SMPTETimeCode alloc] initWithString:@"00:00:00:00"] dClipOut:[[SMPTETimeCode alloc] initWithString:@"00:00:00:00"] dRecIn:[[SMPTETimeCode alloc] initWithString:@"00:00:00:00"] dRecOut:[[SMPTETimeCode alloc] initWithString:@"00:00:00:00"] dReelName:@"A001"dTrackType:@"V" dEditType:@"C" dSlopeR:1.0 dSlopeG:1.0 dSlopeB:1.0 dOffsetR:0.0 dOffsetG:0.0 dOffsetB:0.0 dPowerR:1.0 dPowerG:1.0 dPowerB:1.0 dSaturation:1.0];
}
-(NSString*) getObjectAsString {
    NSMutableString* returnString = [NSMutableString stringWithFormat:@"%d,%@,%@,%@,%@,%d,%d,%d,%@,%@,%@,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n", eventNumber, [clipIn getTimeCode], [clipOut getTimeCode], [recIn getTimeCode], [recOut getTimeCode], frameIn, frameOut, frameCount, reelName, trackType, editType, slopeR, slopeG, slopeB, offsetR, offsetG, offsetB, powerR, powerG, powerB, saturation];
    for (id key in comments) {
        [returnString appendString:[NSString stringWithFormat:@"\n*%@: %@", key, [comments objectForKey:key]]];
    }
    return returnString;
}

-(NSString*) description {
    NSMutableString* returnString = [NSMutableString stringWithFormat:@"%d,%@,%@,%@,%@,%d,%d,%d,%@,%@,%@,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f", eventNumber, [clipIn getTimeCode], [clipOut getTimeCode], [recIn getTimeCode], [recOut getTimeCode], frameIn, frameOut, frameCount, reelName, trackType, editType, slopeR, slopeG, slopeB, offsetR, offsetG, offsetB, powerR, powerG, powerB, saturation];
    for (id key in comments) {
        [returnString appendString:[NSString stringWithFormat:@"  *%@: %@", key, [comments objectForKey:key]]];
    }
    return returnString;
}

-(NSString*) clipInStr {
    return [clipIn getTimeCode];
}
-(void) setClipInStr:(NSString *)clipInStr {
    clipIn = [[SMPTETimeCode alloc] initWithString:clipInStr];
}
-(NSString*) clipOutStr {
    return [clipOut getTimeCode];
}
-(void) setClipOutStr:(NSString *)clipOutStr {
    clipOut = [[SMPTETimeCode alloc] initWithString:clipOutStr];
}
-(NSString*) recInStr {
    return [recIn getTimeCode];
}
-(void) setRecInStr:(NSString *)recInStr {
    recIn = [[SMPTETimeCode alloc] initWithString:recInStr];
}
-(NSString*) recOutStr {
    return [recOut getTimeCode];
}
-(void) setRecOutStr:(NSString *)recOutStr {
    recOut = [[SMPTETimeCode alloc] initWithString:recOutStr];
}
@end
