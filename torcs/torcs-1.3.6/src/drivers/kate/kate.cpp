/***************************************************************************

    file                 : kate.cpp
    created              : 2018. nov. 1., csütörtök, 19:01:02 CET
    copyright            : (C) 2002 Marton Szilagyi

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#ifdef _WIN32
#include <windows.h>
#endif

#include <iostream>
#include <fstream>
#include <string>
#include <stdio.h>
#include <stdlib.h> 
#include <string.h> 
#include <math.h>

#include <tgf.h> 
#include <track.h> 
#include <car.h> 
#include <raceman.h> 
#include <robottools.h>
#include <robot.h>

static tTrack	*curTrack;

static void initTrack(int index, tTrack* track, void *carHandle, void **carParmHandle, tSituation *s); 
static void newrace(int index, tCarElt* car, tSituation *s); 
static void drive(int index, tCarElt* car, tSituation *s); 
static void endrace(int index, tCarElt *car, tSituation *s);
static void shutdown(int index);
static int  InitFuncPt(int index, void *pt); 


/* 
 * Module entry point  
 */ 
extern "C" int 
kate(tModInfo *modInfo) 
{
    memset(modInfo, 0, 10*sizeof(tModInfo));

    modInfo->name    = strdup("kate");		/* name of the module (short) */
    modInfo->desc    = strdup("");	/* description of the module (can be long) */
    modInfo->fctInit = InitFuncPt;		/* init function */
    modInfo->gfId    = ROB_IDENT;		/* supported framework version */
    modInfo->index   = 1;

    return 0; 
} 

/* Module interface initialization. */
static int 
InitFuncPt(int index, void *pt) 
{ 
    tRobotItf *itf  = (tRobotItf *)pt; 

    itf->rbNewTrack = initTrack; /* Give the robot the track view called */ 
				 /* for every track change or new race */ 
    itf->rbNewRace  = newrace; 	 /* Start a new race */
    itf->rbDrive    = drive;	 /* Drive during race */
    itf->rbPitCmd   = NULL;
    itf->rbEndRace  = endrace;	 /* End of the current race */
    itf->rbShutdown = shutdown;	 /* Called before the module is unloaded */
    itf->index      = index; 	 /* Index used if multiple interfaces */
    return 0; 
} 

/* Called for every track change or new race. */
static void  
initTrack(int index, tTrack* track, void *carHandle, void **carParmHandle, tSituation *s) 
{ 
    curTrack = track;
    *carParmHandle = NULL; 
} 

/* Start a new race. */
static void  
newrace(int index, tCarElt* car, tSituation *s) 
{ 
} 

/* Drive during race. */
static void  
drive(int index, tCarElt* car, tSituation *s) 
{
    /*  
     * add the driving code here to modify the 
     * car->_steerCmd 
     * car->_accelCmd 
     * car->_brakeCmd 
     * car->_gearCmd 
     * car->_clutchCmd 
     */
    memset((void *)&car->ctrl, 0, sizeof(tCarCtrl));

    // Uncomment following block comment for training data collection
    /*
    // Heuristics for driving on the center of the road, used for collecting training data
    float heuristic_angle;
    const float SC = 1.0;
    heuristic_angle = RtTrackSideTgAngleL(&(car->_trkPos)) - car->_yaw;
    NORM_PI_PI(heuristic_angle); // put the angle back in the range from -PI to PI
    heuristic_angle -= SC*car->_trkPos.toMiddle/car->_trkPos.seg->width;
    heuristic_angle = heuristic_angle / car->_steerLock;
    car->ctrl.steer = heuristic_angle;
    */

    // Get steering angle from neural network, comment when collecting training data
    std::string line;
    float neuralnet_steering;
    std::ifstream myfile ("/shared_folder/steering.txt");
    getline (myfile,line);
    neuralnet_steering = strtof((line).c_str(),0);
    car->ctrl.steer = neuralnet_steering;

    car->ctrl.gear = 1; // first gear
    car->ctrl.accelCmd = 0.3; // 30% accelerator pedal
    car->ctrl.brakeCmd = 0.0; // no brakes
}

/* End of the current race */
static void
endrace(int index, tCarElt *car, tSituation *s)
{
}

/* Called before the module is unloaded */
static void
shutdown(int index)
{
}

