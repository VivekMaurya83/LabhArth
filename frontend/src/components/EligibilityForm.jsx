/**
 * EligibilityForm — User profile input for eligibility checking.
 *
 * Collects demographic and socioeconomic information
 * needed to check scheme eligibility.
 */

import { useState } from 'react';
import './EligibilityForm.css';

export default function EligibilityForm({ onSubmit, isLoading }) {
  const [profile, setProfile] = useState({
    age: '',
    gender: '',
    state: '',
    category: '',
    income_annual: '',
    occupation: '',
    is_bpl: false,
    is_farmer: false,
    is_student: false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setProfile((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(profile);
  };

  return (
    <form className="eligibility-form" id="eligibility-form" onSubmit={handleSubmit}>
      <h3 className="eligibility-form-title">Your Profile</h3>

      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="age">Age</label>
          <input type="number" id="age" name="age" value={profile.age} onChange={handleChange} placeholder="25" />
        </div>

        <div className="form-group">
          <label htmlFor="gender">Gender</label>
          <select id="gender" name="gender" value={profile.gender} onChange={handleChange}>
            <option value="">Select</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="state">State</label>
          <input type="text" id="state" name="state" value={profile.state} onChange={handleChange} placeholder="e.g., Uttar Pradesh" />
        </div>

        <div className="form-group">
          <label htmlFor="category">Category</label>
          <select id="category" name="category" value={profile.category} onChange={handleChange}>
            <option value="">Select</option>
            <option value="General">General</option>
            <option value="SC">SC</option>
            <option value="ST">ST</option>
            <option value="OBC">OBC</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="income_annual">Annual Income (₹)</label>
          <input type="number" id="income_annual" name="income_annual" value={profile.income_annual} onChange={handleChange} placeholder="200000" />
        </div>

        <div className="form-group">
          <label htmlFor="occupation">Occupation</label>
          <input type="text" id="occupation" name="occupation" value={profile.occupation} onChange={handleChange} placeholder="e.g., Farmer" />
        </div>
      </div>

      <div className="form-checkboxes">
        <label className="checkbox-label">
          <input type="checkbox" name="is_bpl" checked={profile.is_bpl} onChange={handleChange} />
          Below Poverty Line (BPL)
        </label>
        <label className="checkbox-label">
          <input type="checkbox" name="is_farmer" checked={profile.is_farmer} onChange={handleChange} />
          Farmer
        </label>
        <label className="checkbox-label">
          <input type="checkbox" name="is_student" checked={profile.is_student} onChange={handleChange} />
          Student
        </label>
      </div>

      <button type="submit" className="form-submit-btn" disabled={isLoading}>
        {isLoading ? 'Checking...' : 'Check Eligibility'}
      </button>
    </form>
  );
}
