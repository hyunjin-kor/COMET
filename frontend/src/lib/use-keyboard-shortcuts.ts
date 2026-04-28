import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { navigationItems } from '../components/layout/navigation';

/**
 * Whether the active element is something we should not steal keystrokes from.
 *
 * We don't want Alt+1 to navigate away while the user is typing a metal
 * symbol or wt% in a form field.
 */
function isTypingTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  if (target.isContentEditable) return true;
  const tag = target.tagName;
  return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';
}

/**
 * Mounts a single global keydown listener for app-wide shortcuts.
 *
 *  - `Alt+1..5` jump between the five primary workspaces.
 *  - `Shift+?` (i.e. `?`) toggles a transient hint overlay.
 *
 * The hook returns the current overlay-visible state so the parent can
 * render the hint surface without owning its own keyboard wiring.
 */
export function useKeyboardShortcuts(): { hintsVisible: boolean; closeHints: () => void } {
  const navigate = useNavigate();
  const [hintsVisible, setHintsVisible] = useState(false);

  useEffect(() => {
    function handler(event: KeyboardEvent) {
      // Never steal keys while focused inside an editable surface.
      if (isTypingTarget(event.target)) return;
      // Modifier-bearing copy/paste/etc. should not be intercepted.
      if (event.metaKey || event.ctrlKey) return;

      // Alt+digit -> primary navigation.
      if (event.altKey && !event.shiftKey && /^[1-5]$/.test(event.key)) {
        const index = Number(event.key) - 1;
        const target = navigationItems[index];
        if (target) {
          event.preventDefault();
          navigate(target.to);
        }
        return;
      }

      // `?` (Shift+/ on most layouts) toggles the hint overlay.
      if (!event.altKey && event.shiftKey && event.key === '?') {
        event.preventDefault();
        setHintsVisible((current) => !current);
        return;
      }

      // Escape always closes the overlay.
      if (event.key === 'Escape' && hintsVisible) {
        event.preventDefault();
        setHintsVisible(false);
      }
    }

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [navigate, hintsVisible]);

  return { hintsVisible, closeHints: () => setHintsVisible(false) };
}
