import pkg.types.types  as types
from pkg.generic.podDelete.types.types import ExperimentDetails
from pkg.generic.podDelete.environment.environment import GetENV, InitialiseChaosVariables
from pkg.events.events import GenerateEvents
from pkg.status.application import Application
import logging
logger = logging.getLogger(__name__)
from pkg.status.application import Application
from chaosLib.litmus.poddelete.lib.podDelete import PreparePodDelete
from pkg.result.chaosresult import ChaosResults
from pkg.utils.common.common import AbortWatcher

# PodDelete inject the pod-delete chaos
def PodDelete():
	print("1")
	experimentsDetails = ExperimentDetails()
	resultDetails = types.ResultDetails()
	eventsDetails = types.EventDetails()
	chaosDetails = types.ChaosDetails()
	
	status = Application()
	result = ChaosResults()
	
	#Fetching all the ENV passed from the runner pod
	GetENV(experimentsDetails)
	print("2")
	# Intialise the chaos attributes
	InitialiseChaosVariables(chaosDetails, experimentsDetails)
	print("3")
	# Intialise Chaos Result Parameters
	types.SetResultAttributes(resultDetails, chaosDetails)
	logger.info("4")
	#Updating the chaos result in the beginning of experiment
	logger.info("[PreReq]: Updating the chaos result of {} experiment (SOT)".format(experimentsDetails.ExperimentName))
	err = result.ChaosResult(chaosDetails, resultDetails, "SOT")
	if err != None:
		print("Unable to Create the Chaos Result, err: {}".format(err))
		failStep = "Updating the chaos result of pod-delete experiment (SOT)"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails)
		return
	print("5")
	# Set the chaos result uid
	result.SetResultUID(resultDetails, chaosDetails)
	logger.info("6")
	# generating the event in chaosresult to marked the verdict as awaited
	msg = "experiment: " + experimentsDetails.ExperimentName + ", Result: Awaited"
	types.SetResultEventAttributes(eventsDetails, types.AwaitedVerdict, msg, "Normal", resultDetails)
	GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine")

	#DISPLAY THE APP INFORMATION
	print("The application information is as follows", {
		"Namespace": experimentsDetails.AppNS,
		"Label":     experimentsDetails.AppLabel,
		"Ramp Time": experimentsDetails.RampTime,
	})
	print("7")
	
	# Calling AbortWatcher go routine, it will continuously watch for the abort signal and generate the required and result
	AbortWatcher(experimentsDetails.ExperimentName, resultDetails, chaosDetails, eventsDetails)
	print("8")
	# #PRE-CHAOS APPLICATION STATUS CHECK
	print("[Status]: Verify that the AUT (Application Under Test) is running (pre-chaos)")
	err = status.AUTStatusCheck(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.TargetContainer, experimentsDetails.Timeout, experimentsDetails.Delay, chaosDetails)
	if err != None:
		print("Application status check failed, err: %v", err)
		failStep = "Verify that the AUT (Application Under Test) is running (pre-chaos)"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails)
		return
	

	# if experimentsDetails.EngineName != "":
	# 	# marking AUT as running, as we already checked the status of application under test
	# 	msg = "AUT: Running"

	# 	# run the probes in the pre-chaos check
	# 	if len(resultDetails.ProbeDetails) != 0 :

	# 		err = probe.RunProbes(chaosDetails, clients, resultDetails, "PreChaos", eventsDetails):
	# 		if err != None:
	# 			print("Probe Failed, err: %v", err)
	# 			failStep = "Failed while running probes"
	# 			msg = "AUT: Running, Probes: Unsuccessful"
	# 			types.SetEngineEventAttributes(eventsDetails, types.PreChaosCheck, msg, "Warning", chaosDetails)
	# 			GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")
	# 			result.RecordAfterFailure(chaosDetails, resultDetails, failStep, clients, eventsDetails)
	# 			return
			
	# 		msg = "AUT: Running, Probes: Successful"
		
	# 	# generating the for the pre-chaos check
	# 	types.SetEngineEventAttributes(eventsDetails, types.PreChaosCheck, msg, "Normal", chaosDetails)
	# 	GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")
	

	# Including the litmus lib for pod-delete
	if experimentsDetails.ChaosLib == "litmus" :
		err = PreparePodDelete(experimentsDetails, resultDetails, eventsDetails, chaosDetails)
		if err != None:
			print("Chaos injection failed, err: {}".format(err))
			failStep = "failed in chaos injection phase"
			result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails)
			return
		
	else:
		print("[Invalid]: Please Provide the correct LIB")
		failStep = "no match found for specified lib"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails)
		return
	print("9")
	print("[Confirmation]: %v chaos has been injected successfully", experimentsDetails.ExperimentName)
	resultDetails.Verdict = "Pass"

	#POST-CHAOS APPLICATION STATUS CHECK
	print("[Status]: Verify that the AUT (Application Under Test) is running (post-chaos)")
	err = status.AUTStatusCheck(experimentsDetails.AppNS, experimentsDetails.AppLabel, experimentsDetails.TargetContainer, experimentsDetails.Timeout, experimentsDetails.Delay, chaosDetails)
	if err != None:
		print("Application status check failed, err: %v", err)
		failStep = "Verify that the AUT (Application Under Test) is running (post-chaos)"
		result.RecordAfterFailure(chaosDetails, resultDetails, failStep, eventsDetails)
		return
	print("10")
	# if experimentsDetails.EngineName != "" :
	# 	# marking AUT as running, as we already checked the status of application under test
	# 	msg = "AUT: Running"

	# 	# run the probes in the post-chaos check
	# 	if len(resultDetails.ProbeDetails) != 0 :
	# 		err = probe.RunProbes(chaosDetails, clients, resultDetails, "PostChaos", eventsDetails) 
	# 		if err != None:
	# 			print("Probes Failed, err: %v", err)
	# 			failStep = "Failed while running probes"
	# 			msg = "AUT: Running, Probes: Unsuccessful"
	# 			types.SetEngineEventAttributes(eventsDetails, types.PostChaosCheck, msg, "Warning", chaosDetails)
	# 			GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")
	# 			result.RecordAfterFailure(chaosDetails, resultDetails, failStep, clients, eventsDetails)
	# 			return
			
	# 		msg = "AUT: Running, Probes: Successful"
		

	# 	# generating post chaos event
	# 	types.SetEngineEventAttributes(eventsDetails, types.PostChaosCheck, msg, "Normal", chaosDetails)
	# 	GenerateEvents(eventsDetails, clients, chaosDetails, "ChaosEngine")
	

	#Updating the chaosResult in the end of experiment
	print("[The End]: Updating the chaos result of %v experiment (EOT)", experimentsDetails.ExperimentName)
	err = result.ChaosResult(chaosDetails, resultDetails, "EOT")
	if err != None:
		print("Unable to Update the Chaos Result, err: %v", err)
		return
	print("11")

	# generating the event in chaosresult to marked the verdict as pass/fail
	msg = "experiment: " + experimentsDetails.ExperimentName + ", Result: " + resultDetails.Verdict
	reason = types.PassVerdict
	eventType = "Normal"
	if resultDetails.Verdict != "Pass":
		reason = types.FailVerdict
		eventType = "Warning"

	types.SetResultEventAttributes(eventsDetails, reason, msg, eventType, resultDetails)
	GenerateEvents(eventsDetails, chaosDetails, "ChaosResult")
	print("12")
	if experimentsDetails.EngineName != "":
		msg = experimentsDetails.ExperimentName + " experiment has been " + resultDetails.Verdict + "ed"
		types.SetEngineEventAttributes(eventsDetails, types.Summary, msg, "Normal", chaosDetails)
		GenerateEvents(eventsDetails, chaosDetails, "ChaosEngine")
	print("13")