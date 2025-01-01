## Avoiding Scroll Jumps with Absolutely Positioned Hidden Inputs

### Summary
If you visually hide a checkbox (or any focusable element) with `position: absolute` or by clipping it in a container that has `overflow: hidden;`, you might see unexpected scroll jumps or layout shifts when the element is focused. This happens because the browser attempts to ensure the focused element is in view, triggering **scroll anchoring** or reflow.

### Key Points
- **Focus + Scroll Anchoring**: Browsers automatically scroll to keep focused elements visible; off-screen absolute elements can cause layout shifts.
- **Overflow Clipping**: `overflow: hidden` on the parent container can amplify the problem, causing the parent to be repositioned or “jump.”
- **Use SR-Only Instead**: A common fix is the “Screen Reader Only” pattern: tiny (1×1 pixel) or off-screen positioning (`clip: rect(0 0 0 0);`) that fully removes the item from normal layout calculations, preventing scroll anchoring adjustments but keeping it accessible to assistive technologies.

### How to Fix
- **Remove `position: absolute`** for focusable elements, or
- **Use an SR-Only approach** (e.g., `clip: rect(0 0 0 0);` while at `1×1 px` size) so the element has effectively zero layout footprint and doesn’t trigger scroll adjustments.

This ensures the element is still accessible and “visible” to screen readers without causing layout or scroll anchor problems.
