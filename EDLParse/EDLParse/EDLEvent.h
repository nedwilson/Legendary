//
//  EDLEvent.h
//  EDLParse
//
//  Created by Ned Wilson on 10/27/15.
//  Copyright © 2015 Ned Wilson. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "SMPTETimeCode.h"

@interface EDLEvent : NSObject

@property (readwrite) int eventNumber;
@property (strong, readwrite) SMPTETimeCode* clipIn;
@property (strong, readwrite) SMPTETimeCode* clipOut;
@property (strong, readwrite) SMPTETimeCode* recIn;
@property (strong, readwrite) SMPTETimeCode* recOut;
@property (strong, readwrite) NSString* reelName;
@property (strong, readwrite) NSString* trackType;
@property (strong, readwrite) NSString* editType;
@property (readwrite) float slopeR;
@property (readwrite) float slopeG;
@property (readwrite) float slopeB;
@property (readwrite) float offsetR;
@property (readwrite) float offsetG;
@property (readwrite) float offsetB;
@property (readwrite) float powerR;
@property (readwrite) float powerG;
@property (readwrite) float powerB;
@property (readwrite) float saturation;

@property (readwrite) int frameIn;
@property (readwrite) int frameOut;
@property (readwrite) int frameCount;

@property (readwrite) NSDictionary* comments;

@property (strong, readwrite) NSString* clipInStr;
@property (strong, readwrite) NSString* clipOutStr;
@property (strong, readwrite) NSString* recInStr;
@property (strong, readwrite) NSString* recOutStr;

-(id) initWithRecord:(int)mEventNumber dClipIn:(SMPTETimeCode*)mClipIn dClipOut:(SMPTETimeCode*)mClipOut dRecIn:(SMPTETimeCode*)mRecIn dRecOut:(SMPTETimeCode*)mRecOut dReelName:(NSString*)mReelName dTrackType:(NSString*)mTrackType dEditType:(NSString*)mEditType dSlopeR:(float)mSlopeR dSlopeG:(float)mSlopeG dSlopeB:(float)mSlopeB dOffsetR:(float)mOffsetR dOffsetG:(float)mOffsetG dOffsetB:(float)mOffsetB dPowerR:(float)mPowerR dPowerG:(float)mPowerG dPowerB:(float)mPowerB dSaturation:(float)mSaturation;

-(NSString*) getObjectAsString;

@end
