import { CheckCircle2, AlertCircle, XCircle, HelpCircle } from 'lucide-react';
import './EligibilityBadge.css';

/**
 * EligibilityBadge — Displays styled indicator based on eligibility status.
 *
 * Employs clean vectors from Lucide icons and matches them to status colors.
 */
export default function EligibilityBadge({ eligible, text = null }) {
  let statusClass = 'neutral';
  let label = text;
  let IconComponent = HelpCircle;

  // Determine status classification, icon and label text
  if (typeof eligible === 'boolean') {
    statusClass = eligible ? 'success' : 'danger';
    label = label || (eligible ? 'Eligible' : 'Not Eligible');
    IconComponent = eligible ? CheckCircle2 : XCircle;
  } else if (typeof eligible === 'string') {
    const cleanStatus = eligible.trim().toLowerCase();
    if (cleanStatus === 'eligible' || cleanStatus === 'yes') {
      statusClass = 'success';
      label = label || 'Eligible';
      IconComponent = CheckCircle2;
    } else if (cleanStatus === 'partially eligible' || cleanStatus === 'partial' || cleanStatus === 'maybe') {
      statusClass = 'warning';
      label = label || 'Partially Eligible';
      IconComponent = AlertCircle;
    } else {
      statusClass = 'danger';
      label = label || 'Not Eligible';
      IconComponent = XCircle;
    }
  } else {
    label = label || 'Unknown';
  }

  return (
    <span className={`eligibility-badge eligibility-badge--${statusClass}`}>
      <IconComponent size={14} className="eligibility-badge-icon" aria-hidden="true" />
      <span>{label}</span>
    </span>
  );
}
