# Bug Fix: Undo/Redo Stale State Issue

**Bug ID:** UNDO-001  
**Severity:** Critical  
**Date Reported:** August 15, 2026  
**Date Fixed:** August 15, 2026  
**Status:** Fixed  

---

## Summary

Fixed a critical bug where undoing a move action after creating a card would duplicate the card instead of properly moving it back to its original position.

---

## Bug Description

### Reproduction Steps
1. Create a new card in column A
2. Move the card to column B
3. Press Ctrl+Z to undo the move
4. **Expected:** Card moves back to column A
5. **Actual:** A duplicate card appears with the same name

### Root Cause

The action factory functions were capturing the board state at the time the action was created, then using that stale state in the undo/redo functions:

```typescript
// BUGGY CODE
export const moveCardAction = (
  board: BoardData,  // ← Captured at action creation time
  setBoard: (board: BoardData) => void,
  ...
): Action => {
  return {
    undo: async () => {
      await api.moveCard(...);
      
      // Using stale 'board' reference!
      const newColumns = board.columns.map(...);
      setBoard({ ...board, columns: newColumns });
    }
  };
};
```

**The Problem:**
1. When create action is added, it captures board state at time T1
2. When move action is added, it captures board state at time T2
3. When undo is called, it uses the stale T2 state
4. This stale state doesn't include the card in the new column
5. Result: Card gets duplicated instead of moved

---

## The Fix

Changed all action factory functions to use **functional setState** which always receives the current state:

```typescript
// FIXED CODE
export const moveCardAction = (
  board: BoardData,
  setBoard: React.Dispatch<React.SetStateAction<BoardData | null>>,
  ...
): Action => {
  return {
    undo: async () => {
      await api.moveCard(...);
      
      // Using functional setState to get current state!
      setBoard((prevBoard) => {
        if (!prevBoard) return prevBoard;
        
        const newColumns = prevBoard.columns.map(...);
        return { ...prevBoard, columns: newColumns };
      });
    }
  };
};
```

**Why This Works:**
1. `setBoard((prevBoard) => ...)` receives the CURRENT state
2. No stale state references
3. Always operates on the latest board data
4. Null check added for safety

---

## Files Modified

1. `frontend/src/lib/actionFactory.ts`
   - Updated all 5 action factory functions
   - Changed setBoard parameter type to `React.Dispatch<React.SetStateAction<BoardData | null>>`
   - Added functional setState to all undo/redo functions
   - Added null checks in all setState callbacks

---

## Changes Made

### 1. Type Signature Changes

**Before:**
```typescript
setBoard: (board: BoardData) => void
```

**After:**
```typescript
setBoard: React.Dispatch<React.SetStateAction<BoardData | null>>
```

### 2. setState Pattern Changes

**Before:**
```typescript
setBoard({
  ...board,  // ← Stale state!
  columns: newColumns,
});
```

**After:**
```typescript
setBoard((prevBoard) => {
  if (!prevBoard) return prevBoard;
  
  return {
    ...prevBoard,  // ← Current state!
    columns: newColumns,
  };
});
```

### 3. Functions Updated

- ✅ `createCardAction` - undo and redo
- ✅ `deleteCardAction` - undo and redo
- ✅ `moveCardAction` - undo and redo (the critical one!)
- ✅ `updateCardAction` - undo and redo
- ✅ `renameColumnAction` - undo and redo

**Total:** 10 undo/redo functions fixed

---

## Testing

### Test Case 1: Original Bug
1. Create card "Test"
2. Move to another column
3. Press Ctrl+Z
4. **Result:** ✅ Card moves back (no duplication)

### Test Case 2: Multiple Actions
1. Create card "A"
2. Create card "B"
3. Move card "A" to column 2
4. Move card "B" to column 3
5. Press Ctrl+Z twice
6. **Result:** ✅ Both cards move back correctly

### Test Case 3: Edit Then Move
1. Create card "Test"
2. Edit card to "Test 2"
3. Move card to column 2
4. Press Ctrl+Z (undo move)
5. Press Ctrl+Z (undo edit)
6. **Result:** ✅ Card moves back, then title reverts

### Test Case 4: Delete Then Undo
1. Create card "Test"
2. Delete card
3. Press Ctrl+Z
4. **Result:** ✅ Card restored correctly

### Test Case 5: Complex Sequence
1. Create 3 cards
2. Move all 3 to different columns
3. Edit one card
4. Delete one card
5. Press Ctrl+Z 5 times
6. **Result:** ✅ All actions undone correctly

---

## Impact Analysis

### Before Fix
- ❌ Undo/redo was unreliable
- ❌ Cards could be duplicated
- ❌ State could become inconsistent
- ❌ Users lost trust in undo feature

### After Fix
- ✅ Undo/redo works correctly
- ✅ No card duplication
- ✅ State always consistent
- ✅ Users can trust undo feature

---

## Lessons Learned

1. **Never capture mutable state in closures** - Always use functional setState when state might change
2. **React setState has two forms** - Direct value and functional updater
3. **Functional setState is safer** - Always receives current state
4. **Test complex sequences** - Simple tests might not catch stale state bugs
5. **Null checks are important** - TypeScript caught the null issue

---

## Related Issues

- None (first occurrence of this bug pattern)

---

## Prevention

To prevent similar bugs in the future:

1. **Always use functional setState** when:
   - State is captured in closures
   - Multiple state updates might happen
   - Async operations are involved

2. **Code review checklist:**
   - ✅ Check for stale state references
   - ✅ Verify functional setState usage
   - ✅ Test complex action sequences
   - ✅ Verify null handling

3. **Testing guidelines:**
   - Test multi-step sequences
   - Test undo/redo chains
   - Test interleaved actions
   - Test edge cases

---

## Performance Impact

**Before:** Same performance  
**After:** Same performance (functional setState has no overhead)

---

## Backward Compatibility

✅ No breaking changes  
✅ Existing functionality preserved  
✅ Only internal implementation changed

---

## Deployment Notes

- No database changes required
- No API changes required
- Frontend-only fix
- Safe to deploy immediately

---

## Verification

**Build Status:** ✅ Passing  
**TypeScript:** ✅ No errors  
**Manual Testing:** ✅ All test cases pass  
**Regression Testing:** ✅ No regressions found

---

## Conclusion

This was a critical bug caused by stale state references in closures. The fix uses React's functional setState pattern to always operate on current state. All undo/redo operations now work correctly.

**Status:** ✅ Fixed and verified  
**Risk Level:** Low (well-tested fix)  
**Ready for Production:** Yes

---

**Fixed By:** AI Assistant  
**Reviewed By:** User (reported the bug)  
**Date:** August 15, 2026
