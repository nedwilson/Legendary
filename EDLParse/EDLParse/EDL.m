//
//  EDL.m
//  EDLParse
//
//  Created by Ned Wilson on 10/27/15.
//  Copyright © 2015 Ned Wilson. All rights reserved.
//

#import "EDL.h"

@implementation EDL

@synthesize edlFilePath = _edlFilePath;
@synthesize edlEventList = _edlEventList;
@synthesize edlHeaders = _edlHeaders;

-(id) initWithPath:(NSString *)edlPath {
    if (self = [super init]) {
        NSFileManager* fm = [[NSFileManager alloc] init];
        if ([fm fileExistsAtPath:edlPath]) {
            if (![fm isReadableFileAtPath:edlPath]) {
                NSException* wtf = [NSException exceptionWithName:@"ERROR:EDL.m"
                                                           reason:[NSString stringWithFormat:@"EDL File Provided \"%@\": Unable to read. Permission Denied.", edlPath]
                                                         userInfo:nil];
                @throw wtf;
            }
            NSDictionary *attrs = [fm attributesOfItemAtPath:edlPath error:NULL];
            unsigned long long result = [attrs fileSize];
            if (result == 0) {
                NSException* wtf = [NSException exceptionWithName:@"ERROR:EDL.m"
                                                           reason:[NSString stringWithFormat:@"EDL File Provided \"%@\" is zero bytes in length.", edlPath]
                                                         userInfo:nil];
                @throw wtf;
            }
            _edlFilePath = edlPath;
        } else {
            NSException* wtf = [NSException exceptionWithName:@"ERROR:EDL.m"
                                                       reason:[NSString stringWithFormat:@"EDL File Provided \"%@\" does not exist.", edlPath]
                                                     userInfo:nil];
            @throw wtf;
            
        }
    } else {
        NSException* wtf = [NSException exceptionWithName:@"ERROR:EDL.m"
                                                   reason:@"Unable to initialize super class."
                                                 userInfo:nil];
        @throw wtf;
    }
    return self;
}

-(id) init {
    return [self initWithPath:@""];
}

-(void) parse {
    NSError* error = NULL;
    NSString* fileContents = [NSString stringWithContentsOfFile:_edlFilePath encoding:NSASCIIStringEncoding error:&error];
    if (fileContents == nil) {
        NSException* wtf = [NSException exceptionWithName:@"ERROR:EDL.m"
                                                   reason:[NSString stringWithFormat:@"Unable to read file provided: \"%@\". \nMessage: %@", _edlFilePath, [error localizedFailureReason]]
                                                 userInfo:nil];
        @throw wtf;
    }
    
    // Break the EDL file into lines
    int i = 0;
    unichar firstChar = 0;
    NSArray *edl_file_lines = [fileContents componentsSeparatedByCharactersInSet:[NSCharacterSet newlineCharacterSet]];
    NSMutableDictionary *headers = [[NSMutableDictionary alloc] init];
    NSMutableDictionary *event_comments = nil;
    NSMutableArray *events = [[NSMutableArray alloc] init];
    
    NSCharacterSet *capitalLetters = [NSCharacterSet uppercaseLetterCharacterSet];
    NSCharacterSet *digits = [NSCharacterSet decimalDigitCharacterSet];
    NSCharacterSet *comments = [NSCharacterSet characterSetWithCharactersInString:@"*"];
    NSMutableCharacterSet *colsep = [NSMutableCharacterSet characterSetWithCharactersInString:@"(,)"];
    NSMutableCharacterSet *eventvalid = [NSMutableCharacterSet characterSetWithCharactersInString:@"_.-/:"];
    [eventvalid formUnionWithCharacterSet:[NSCharacterSet alphanumericCharacterSet]];
    [colsep formUnionWithCharacterSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];

    EDLEvent *currentEvent = nil;
    
    for (i = 0; i < [edl_file_lines count]; i++) {
        firstChar = [edl_file_lines[i] characterAtIndex:0];
        // first character is a capital letter? this is a header line.
        // split on ':'
        if ([capitalLetters characterIsMember:firstChar]) {
            NSArray *header_line = [edl_file_lines[i] componentsSeparatedByString:@":"];
            if ([header_line count] < 2) {
                NSLog(@"WARNING: Unexpected EDL Header Line: %@", edl_file_lines[i]);
                continue;
            }
            [headers setObject:[(NSString*)header_line[1] stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]] forKey:[(NSString*)header_line[0] stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]]];
           
        // first character is a digit? this is an event declaration.
        // split on whitespace.
        } else if ([digits characterIsMember:firstChar]) {
            currentEvent = [[EDLEvent alloc] init];
            event_comments = [[NSMutableDictionary alloc] init];
            [currentEvent setComments:event_comments];
            NSMutableArray* event_line = [[NSMutableArray alloc] init];
            NSScanner *scanner = [NSScanner scannerWithString:edl_file_lines[i]];
            NSString *tmptoken = nil;

            while (![scanner isAtEnd]) {
                if ([scanner scanCharactersFromSet:eventvalid intoString:&tmptoken]) {
                    [event_line addObject:tmptoken];
                } else {
                    [scanner setScanLocation: [scanner scanLocation]+1];
                }
            }
            
            [currentEvent setEventNumber:[[event_line objectAtIndex:0] intValue]];
            [currentEvent setReelName:event_line[1]];
            [currentEvent setTrackType:event_line[2]];
            [currentEvent setEditType:event_line[3]];
            [currentEvent setClipInStr:event_line[4]];
            [currentEvent setClipOutStr:event_line[5]];
            [currentEvent setRecInStr:event_line[6]];
            [currentEvent setRecOutStr:event_line[7]];
            [events addObject:currentEvent];
        // first character is an asterisk? this is an event comment.
        // split on ':'
        } else if ([comments characterIsMember:firstChar]) {
            NSArray *comment_line = nil;
            if ([edl_file_lines[i] hasPrefix:@"*ASC"]) {
                comment_line = @[[edl_file_lines[i] substringToIndex:8], [edl_file_lines[i] substringFromIndex:9]];
            } else {
                NSRange range = [edl_file_lines[i] rangeOfString:@":"];
                comment_line = @[[edl_file_lines[i] substringToIndex:range.location], [edl_file_lines[i] substringFromIndex:range.location+1]];
            }
            if ([comment_line count] < 2) {
                NSLog(@"WARNING: Unexpected EDL Event Comment Line: %@", edl_file_lines[i]);
                continue;
            }
            if (currentEvent == nil || event_comments == nil) {
                NSLog(@"WARNING: currentEvent or event_comments are nil. Something is amiss.");
                continue;
            }
            NSString* tmp_comment_name = [comment_line[0] substringFromIndex:1];
            [(NSMutableDictionary*)[currentEvent comments] setObject:[(NSString*)comment_line[1] stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]] forKey:tmp_comment_name];
            if ([tmp_comment_name  isEqualToString: @"ASC_SOP"]) {
                NSArray* asc_sop_tmp = [(NSString*)comment_line[1] componentsSeparatedByCharactersInSet:colsep];
                asc_sop_tmp = [asc_sop_tmp filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"self <> ''"]];
                [currentEvent setSlopeR:[asc_sop_tmp[0] floatValue]];
                [currentEvent setSlopeG:[asc_sop_tmp[1] floatValue]];
                [currentEvent setSlopeB:[asc_sop_tmp[2] floatValue]];
                [currentEvent setOffsetR:[asc_sop_tmp[3] floatValue]];
                [currentEvent setOffsetG:[asc_sop_tmp[4] floatValue]];
                [currentEvent setOffsetB:[asc_sop_tmp[5] floatValue]];
                [currentEvent setPowerR:[asc_sop_tmp[6] floatValue]];
                [currentEvent setPowerG:[asc_sop_tmp[7] floatValue]];
                [currentEvent setPowerB:[asc_sop_tmp[8] floatValue]];
            } else if ([tmp_comment_name isEqualToString:@"ASC_SAT"]) {
                [currentEvent setSaturation:[comment_line[1] floatValue]];
            }
        }

    }
    _edlEventList = events;
    _edlHeaders = headers;
    // NSLog(@"Headers: %@", _edlHeaders);
    // NSLog(@"Event List: %@", _edlEventList);
    return;
}

@end
