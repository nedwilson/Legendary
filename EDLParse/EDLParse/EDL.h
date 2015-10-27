//
//  EDL.h
//  EDLParse
//
//  Created by Ned Wilson on 10/27/15.
//  Copyright © 2015 Ned Wilson. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "EDLEvent.h"

@interface EDL : NSObject

@property (readonly) NSString* edlFilePath;
@property (readonly) NSArray* edlEventList;
@property (readonly) NSDictionary* edlHeaders;

-(id) initWithPath:(NSString*)edlPath;
-(void) parse;

@end
