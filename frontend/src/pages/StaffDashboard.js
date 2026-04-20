import { useEffect, useState } from "react";
import API from "../services/api";
import Navbar from "../components/Navbar";
import NotificationsPanel from "../components/NotificationsPanel";

function StaffDashboard() {
  const user = JSON.parse(localStorage.getItem("user"));

  const [hospital, setHospital] = useState(null);
  const [requests, setRequests] = useState([]);
  const [message, setMessage] = useState("");
  const [organs, setOrgans] = useState([]);
  

  const [hospitalForm, setHospitalForm] = useState({
    name: "",
    address: ""
  });

  const [staffForm, setStaffForm] = useState({
    name: "",
    role: "",
    specialization: "",
    phone: ""
  });

  const [requestUpdate, setRequestUpdate] = useState({
    request_id: "",
    status: "",
    notes: ""
  });

  const [transplantForm, setTransplantForm] = useState({
    match_id: "",
    surgery_date: "",
    outcome: "",
    surgeon_id: ""
  });

  const loadOrgans = async () => {
    try {
      const res = await API.get("/organs");
      setOrgans(res.data || []);
    } catch {
      setOrgans([]);
    }
  };

  const loadHospital = async () => {
    try {
      const res = await API.get(`/hospital/profile/${user.user_id}`);
      setHospital(res.data);
    } catch {
      setHospital(null);
    }
  };

  const loadRequests = async () => {
    try {
      const res = await API.get("/requests/details");
      setRequests(res.data || []);
    } catch {
      setRequests([]);
    }
  };

  useEffect(() => {
    loadHospital();
    loadRequests();
    loadOrgans(); // 
  }, []);

  const createHospital = async () => {
    try {
      const res = await API.post("/hospital/profile", {
        ...hospitalForm,
        user_id: user.user_id
      });
      setMessage(res.data.message || "Hospital created successfully");
      loadHospital();
    } catch (err) {
      setMessage(err?.response?.data?.error || "Failed to create hospital");
    }
  };

  const addStaff = async () => {
    try {
      if (!hospital) {
        setMessage("Create hospital first");
        return;
      }

      const res = await API.post("/staff", {
        ...staffForm,
        hospital_id: hospital.hospital_id
      });

      setMessage(res.data.message || "Staff added successfully");
      setStaffForm({
        name: "",
        role: "",
        specialization: "",
        phone: ""
      });
    } catch (err) {
      setMessage(err?.response?.data?.error || "Failed to add staff");
    }
  };

  const updateRequest = async () => {
    try {
      const res = await API.put(`/requests/${requestUpdate.request_id}/status`, {
        status: requestUpdate.status,
        notes: requestUpdate.notes
      });

      setMessage(res.data.message || "Request updated successfully");
      loadRequests();
    } catch (err) {
      setMessage(err?.response?.data?.error || "Failed to update request");
    }
  };

  const addTransplant = async () => {
    try {
      if (!hospital) {
        setMessage("Create hospital first");
        return;
      }

      const res = await API.post("/transplants", {
        ...transplantForm,
        hospital_id: hospital.hospital_id
      });

      setMessage(res.data.message || "Transplant recorded successfully");
      setTransplantForm({
        match_id: "",
        surgery_date: "",
        outcome: "",
        surgeon_id: ""
      });
    } catch (err) {
      setMessage(err?.response?.data?.error || "Failed to record transplant");
    }
  };

  const runMatch = async (organId) => {
    try {
      const res = await API.post(`/match/${organId}`);
      const user = JSON.parse(localStorage.getItem("user"));

      approved_by: user.user_id
  
      await API.post("/matches/approve", {
        request_id: res.data.request_id,
        organ_id: organId,
        score: res.data.score,        
        approved_by: 1                
      });
  
      alert("Match found and saved!");
  
    } catch (err) {
      if (err.response && err.response.status === 404) {
        alert("No match found");
      } else {
        console.log(err);
        alert("Something went wrong");
      }
    }
  };

  return (
    <div className="page-container">
      <Navbar />

      <div className="recipient-layout">
        <div className="left-column">
          {!hospital ? (
            <div className="card">
              <h2 className="page-title">Register Hospital</h2>
              <p className="muted-text">
                Register hospital once. After that, hospital details will appear here.
              </p>

              <div className="form-grid">
                <input
                  className="input"
                  placeholder="Hospital Name"
                  value={hospitalForm.name}
                  onChange={(e) => setHospitalForm({ ...hospitalForm, name: e.target.value })}
                />
                <input
                  className="input"
                  placeholder="Address"
                  value={hospitalForm.address}
                  onChange={(e) => setHospitalForm({ ...hospitalForm, address: e.target.value })}
                />
              </div>

              <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={createHospital}>
                Register Hospital
              </button>
            </div>
          ) : (
            <div className="card">
              <h2 className="page-title">Hospital Details</h2>
              <div className="details-grid">
                <div className="detail-box">
                  <span className="detail-label">Hospital ID</span>
                  <span className="detail-value">{hospital.hospital_id}</span>
                </div>
                <div className="detail-box">
                  <span className="detail-label">Name</span>
                  <span className="detail-value">{hospital.name}</span>
                </div>
                <div className="detail-box detail-box-wide">
                  <span className="detail-label">Address</span>
                  <span className="detail-value">{hospital.address}</span>
                </div>
              </div>
            </div>
          )}

          <NotificationsPanel />
        </div>

        <div className="right-column">
          <div className="card">
            <h2 className="page-title">Add Staff</h2>
            <p className="muted-text">
              You can add multiple staff members. Same hospital cannot register the same role + specialization combination twice.
            </p>

            <div className="form-row">
              <input
                className="input"
                placeholder="Name"
                value={staffForm.name}
                onChange={(e) => setStaffForm({ ...staffForm, name: e.target.value })}
              />
              <input
                className="input"
                placeholder="Role"
                value={staffForm.role}
                onChange={(e) => setStaffForm({ ...staffForm, role: e.target.value })}
              />
              <input
                className="input"
                placeholder="Specialization"
                value={staffForm.specialization}
                onChange={(e) => setStaffForm({ ...staffForm, specialization: e.target.value })}
              />
              <input
                className="input"
                placeholder="Phone"
                value={staffForm.phone}
                onChange={(e) => setStaffForm({ ...staffForm, phone: e.target.value })}
              />
            </div>

            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={addStaff}>
              Add Staff
            </button>
          </div>

          <div className="card" style={{ marginTop: 20 }}>
            <h2 className="page-title">Requests Overview</h2>

            {requests.length === 0 ? (
              <p className="muted-text">No requests found.</p>
            ) : (
              <div className="list-box">
                {requests.map((req) => (
                  <div className="request-card" key={req.request_id}>
                    <div className="request-top">
                      <div>
                        <h3 className="request-title">Request #{req.request_id}</h3>
                        <p className="muted-text">Recipient: {req.recipient_name || "-"}</p>
                        <p className="muted-text">Donor: {req.donor_name || "Not matched yet"}</p>
                        <p className="muted-text">Organ: {req.organ_needed}</p>
                        <p className="muted-text">Urgency: {req.urgency_level}</p>
                        <p className="muted-text">Notes: {req.notes || "-"}</p>
                        <p className="muted-text">Match ID: {req.match_id || "-"}</p>
                      </div>
                      <span className="badge">{req.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card" style={{ marginTop: 20 }}>
            <h2 className="page-title">Update Request Status</h2>

            <div className="form-grid">
              <input
                className="input"
                placeholder="Request ID"
                value={requestUpdate.request_id}
                onChange={(e) => setRequestUpdate({ ...requestUpdate, request_id: e.target.value })}
              />

              <select
                className="select"
                value={requestUpdate.status}
                onChange={(e) => setRequestUpdate({ ...requestUpdate, status: e.target.value })}
              >
                <option value="">Select Status</option>
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
                <option value="Completed">Completed</option>
              </select>

              <textarea
                className="input"
                rows="4"
                placeholder="Notes"
                value={requestUpdate.notes}
                onChange={(e) => setRequestUpdate({ ...requestUpdate, notes: e.target.value })}
              />
            </div>

            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={updateRequest}>
              Update Request
            </button>
          </div>

          <div className="card" style={{ marginTop: 20 }}>
            <h2 className="page-title">Record Surgery / Transplant</h2>

            <div className="form-grid">
              <input
                className="input"
                placeholder="Match ID"
                value={transplantForm.match_id}
                onChange={(e) => setTransplantForm({ ...transplantForm, match_id: e.target.value })}
              />

              <input
                className="input"
                type="date"
                value={transplantForm.surgery_date}
                onChange={(e) => setTransplantForm({ ...transplantForm, surgery_date: e.target.value })}
              />

              <input
                className="input"
                placeholder="Outcome"
                value={transplantForm.outcome}
                onChange={(e) => setTransplantForm({ ...transplantForm, outcome: e.target.value })}
              />

              <input
                className="input"
                placeholder="Surgeon ID"
                value={transplantForm.surgeon_id}
                onChange={(e) => setTransplantForm({ ...transplantForm, surgeon_id: e.target.value })}
              />
            </div>

            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={addTransplant}>
              Record Surgery
            </button>

            <div style={{ marginTop: 16 }}>
  <h3>Select Organ to Match</h3>

  {organs.length === 0 ? (
    <p className="muted-text">No available organs</p>
  ) : (
    organs.map((org) => (
      <div key={org.organ_id} style={{ marginBottom: 8 }}>
        <span>
          {org.organ_type} ({org.blood_group})
        </span>

        <button
          style={{ marginLeft: 10 }}
          onClick={() => runMatch(org.organ_id)}
        >
          Run Matching
        </button>
      </div>
    ))
  )}
</div>
          </div>

          {message && <p style={{ marginTop: 14 }} className="success-text">{message}</p>}
        </div>
      </div>
    </div>
  );
}

export default StaffDashboard;