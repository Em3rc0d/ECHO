# MK2 Incident Evidence

**Status:** `SCHEMA_READY / EMPTY UNTIL INCIDENTS OR DRILLS`

## Purpose

Turn operational failures and exercises into reusable evidence instead of one-time fixes.

## Record template

Incident ID/date; affected release/sources; detection mechanism; timeline; user/system impact; relevant metrics/log refs; root-cause category; immediate containment; permanent correction; new/updated risk IDs; regression/fault test added; certificates/models/configs invalidated; closure evidence.

## Categories

Source/network, decode, scheduler/capacity, model/quality, EventEngine, broker/delivery, storage, security, privacy, configuration/release and external dependency.

## Privacy

Incident notes redact credentials and unnecessary personal/audio content. Evidence follows retention/access policy.

## Learning rule

A resolved defect is not fully closed until a control/test makes recurrence detectable or prevents it where practical.

## Current state

Planned tabletop/chaos exercises can create incident-like evidence before production; they are labeled `DRILL`, not real incident.