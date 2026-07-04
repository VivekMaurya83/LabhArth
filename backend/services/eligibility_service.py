"""
LabhArth AI — Eligibility Service
====================================
Business logic for eligibility determination.
"""

from typing import Any
from uuid import UUID

from backend.services.scheme_service import SchemeService
from backend.utils.logger import logger


class EligibilityService:
    """
    Service layer for eligibility checking.
    """

    def __init__(self):
        self.scheme_service = SchemeService()
        logger.info("EligibilityService initialized")

    def _evaluate_rule(self, field_value: Any, operator: str, rule_value: Any) -> bool:
        """Helper to evaluate standard operators against user profile values."""
        try:
            if operator == "eq":
                return field_value == rule_value
            elif operator == "neq":
                return field_value != rule_value
            elif operator == "gt":
                return float(field_value) > float(rule_value)
            elif operator == "gte":
                return float(field_value) >= float(rule_value)
            elif operator == "lt":
                return float(field_value) < float(rule_value)
            elif operator == "lte":
                return float(field_value) <= float(rule_value)
            elif operator == "in":
                if isinstance(rule_value, list):
                    # Handle case-insensitive check if it's a string
                    if isinstance(field_value, str):
                        return any(str(item).strip().lower() == field_value.strip().lower() for item in rule_value)
                    return field_value in rule_value
                return str(field_value).strip().lower() == str(rule_value).strip().lower()
            elif operator == "not_in":
                if isinstance(rule_value, list):
                    if isinstance(field_value, str):
                        return not any(str(item).strip().lower() == field_value.strip().lower() for item in rule_value)
                    return field_value not in rule_value
                return str(field_value).strip().lower() != str(rule_value).strip().lower()
            elif operator == "exists":
                return field_value is not None
            return False
        except Exception as e:
            logger.warning(f"Error evaluating rule operator={operator}, val={field_value}, rule_val={rule_value}: {e}")
            return False

    async def check_eligibility(
        self,
        scheme_id: UUID,
        user_profile: dict,
    ) -> dict:
        """
        Determine if a user is eligible for a specific scheme based on its structured rules.

        Args:
            scheme_id: UUID of the scheme to check
            user_profile: User profile data

        Returns:
            Eligibility result with reasoning
        """
        logger.info(f"Checking eligibility: scheme={scheme_id}")

        # Fetch scheme details
        scheme = await self.scheme_service.get_scheme_details(scheme_id)
        if not scheme:
            raise ValueError(f"Scheme with ID {scheme_id} not found.")

        criteria = scheme.get("eligibility_criteria") or {}
        rules = criteria.get("rules") or []
        required_docs = scheme.get("required_documents") or []

        passed_rules = []
        failed_rules = []
        unresolved_rules = []

        # Standard profile mappings to handle minor differences
        profile_cleaned = {}
        for k, v in user_profile.items():
            # Clean keys to lowercase and replace spaces/dashes with underscores
            k_clean = k.strip().lower().replace(" ", "_").replace("-", "_")
            profile_cleaned[k_clean] = v

        for rule in rules:
            field = rule.get("field")
            if not field:
                continue

            field_clean = field.strip().lower().replace(" ", "_").replace("-", "_")
            operator = rule.get("operator")
            rule_value = rule.get("value")
            label = rule.get("label") or f"{field} {operator} {rule_value}"

            # Check if required field exists in the user profile
            if field_clean not in profile_cleaned or profile_cleaned[field_clean] is None:
                # If field is missing from profile, it's unresolved
                unresolved_rules.append({
                    "field": field,
                    "operator": operator,
                    "value": rule_value,
                    "label": label,
                    "reason": f"Missing required profile field: '{field}'"
                })
                continue

            user_value = profile_cleaned[field_clean]

            # Special case boolean checks: if rule_value is true/false, check truthiness
            if isinstance(rule_value, bool):
                # Normalize string representations of boolean if necessary
                if isinstance(user_value, str):
                    user_value = user_value.strip().lower() in ("true", "yes", "1")
                elif not isinstance(user_value, bool):
                    user_value = bool(user_value)

            # Evaluate rule
            if self._evaluate_rule(user_value, operator, rule_value):
                passed_rules.append({
                    "field": field,
                    "label": label,
                    "user_value": user_value
                })
            else:
                failed_rules.append({
                    "field": field,
                    "operator": operator,
                    "value": rule_value,
                    "label": label,
                    "user_value": user_value,
                    "reason": f"Profile field '{field}' with value '{user_value}' failed criteria: '{label}'"
                })

        # Calculate eligibility status
        if failed_rules:
            status = "Not Eligible"
            reasoning = f"User profile does not meet the eligibility requirements for '{scheme['name']}'."
        elif unresolved_rules:
            status = "Partially Eligible"
            reasoning = "User profile meets all provided criteria, but missing fields prevent complete evaluation."
        else:
            status = "Eligible"
            reasoning = f"User profile fully satisfies all eligibility requirements for '{scheme['name']}'."

        # Compile reasons
        reasons = []
        if failed_rules:
            reasons.extend([r["reason"] for r in failed_rules])
        if unresolved_rules:
            reasons.extend([r["reason"] for r in unresolved_rules])
        if status == "Eligible":
            reasons.append("All profile criteria successfully matched against the scheme rules.")

        # Calculate confidence score
        total_rules = len(rules)
        if total_rules == 0:
            confidence = 1.0
        else:
            # High confidence if fully eligible or definitely not eligible. Low if partially/missing.
            if status == "Eligible":
                confidence = 1.0
            elif status == "Not Eligible":
                confidence = 0.95  # Confident they don't qualify
            else:
                confidence = len(passed_rules) / total_rules

        return {
            "scheme_id": str(scheme_id),
            "scheme_name": scheme["name"],
            "eligibility_status": status,
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "reasons": reasons,
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
            "missing_criteria": unresolved_rules,
            "required_documents": required_docs if status in ("Eligible", "Partially Eligible") else []
        }
