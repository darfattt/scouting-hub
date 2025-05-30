# Wyscout Position Detection Fix

## Issue Identified

The position filtering is not working correctly because the system is not properly detecting outfield players from your Wyscout data.

## Root Cause

Looking at your data, I can see:

1. **Goalkeeper files** have columns: `Saves`, `Conceded goals`, `Shots against`
2. **Outfield files** have columns: `Goals`, `Assists`, `Passes`, `Position`
3. **Position codes** in Wyscout format: `CF`, `LAMF`, `RCMF3`, etc.

The issue is in the data detection logic - it's not properly identifying outfield vs goalkeeper data.

## Solution

I need to fix the `OutfieldDataProcessor` to:

1. **Better detect outfield data** vs goalkeeper data
2. **Properly parse Wyscout position codes**
3. **Handle multiple positions** in one field (e.g., "CF, LAMF")

## Quick Fix

Let me create a working version that properly handles your Wyscout data structure.

## Expected Results

After the fix, you should see:
- ✅ **Goalkeepers**: 35+ players
- ✅ **Forwards**: 5+ players (CF, RWF, LWF, LAMF, RAMF, etc.)
- ✅ **Midfielders**: Players with LCMF3, RCMF3, etc.
- ✅ **Defenders**: 2+ players

## Files to Update

1. `data_processor.py` - Fix outfield data detection
2. `rag_system.py` - Ensure position filters work correctly
3. Test with actual data to verify

The system should then properly build RAG systems for all available position types in your Wyscout data.
