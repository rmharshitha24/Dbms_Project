import { useEffect, useState } from "react";
import API from "../services/api";
import Navbar from "../components/Navbar";
import NotificationsPanel from "../components/NotificationsPanel";

const ORGAN_OPTIONS = [
  "Kidney",
  "Liver",
  "Heart",
  "Lung",
  "Pancreas",
  "Cornea",
  "Intestine",
  "Skin",
  "Bone Marrow"
];

function RecipientDashboard() {
  const user = JSON.parse(localStorage.getItem("user"));

  const [profile, setProfile] = useState(null);
  const [hospitals, setHospitals] = useState([]);
  const [requests, setRequests] = useState([]);
  const [message, setMessage] = useState("");

  const [profileForm, setProfileForm] = useState({
    name: "",
    dob: "",
    blood_group: "",
    gender: "",
    phone: "",
    address: "",
    hospital_id: ""
  });

  const [requestForm, setRequestForm] = useState({
    organ_needed: "",
    urgency_level: ""
  });

  const loadHospitals = async () => {
    try {
      const res = await API.get("/hospital");
      setHospitals(res.data || []);
    } catch {
      setHospitals([]);
    }
  };

  const loadProfile = async () => {
    try {
      const res = await API.get(`/recipients/profile/${user.user_id}`);
      setProfile(res.data);
      loadRequests(res.data.recipient_id);
    } catch {
      setProfile(null);
    }
  };

  const loadRequests = async (recipientId) => {
    try {
      const res = await API.get(`/requests/recipient/${recipientId}`);
      setRequests(res.data || []);
    } catch {
      setRequests([]);
    }
  };

  useEffect(() => {
    loadHospitals();
    loadProfile();
  }, []);

  const createProfile = async () => {
    try {
      const res = await API.post("/recipients/profile", {
        ...profileForm,
        user_id: user.user_id
      });
      setMessage(res.data.message || "Recipient profile created successfully");
      loadProfile();
    } catch (err) {
      setMessage(err?.response?.data?.error || "Failed to create recipient profile");
    }
  };

  const createRequest = async () => {
    try {
      if (!profile) {
        setMessage("Please complete recipient registration first");
        return;
      }

      const res = await API.post("/requests", {
        ...requestForm,
        recipient_id: profile.recipient_id
      });

      setMessage(res.data.message || "Request created successfully");
      setRequestForm({
        organ_needed: "",
        urgency_level: ""
      });
      loadRequests(profile.recipient_id);
    } catch (err) {
      setMessage(err?.response?.data?.error || "Failed to create request");
    }
  };

  const updateUrgency = async (requestId, urgency) => {
    try {
      const res = await API.put(`/requests/${requestId}/urgency`, {
        urgency_level: urgency
      });
      setMessage(res.data.message || "Urgency updated successfully");
      loadRequests(profile.recipient_id);
    } catch (err) {
      setMessage(err?.response?.data?.error || "Failed to update urgency");
    }
  };

  const deleteRequest = async (requestId) => {
    try {
      const res = await API.delete(`/requests/${requestId}`);
      setMessage(res.data.message || "Request deleted successfully");
      loadRequests(profile.recipient_id);
    } catch (err) {
      setMessage(err?.response?.data?.error || "Failed to delete request");
    }
  };

  return (
    <div className="page-container">
      <Navbar />

      <div className="recipient-layout">
        <div className="left-column">
          {!profile ? (
            <div className="card">
              <h2 className="page-title">Recipient Registration</h2>
              <p className="muted-text">
                Register once. After that, your details will be shown here and you can keep creating requests.
              </p>

              <div className="form-row">
                <input
                  className="input"
                  placeholder="Full Name"
                  value={profileForm.name}
                  onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                />

                <input
                  className="input"
                  type="date"
                  value={profileForm.dob}
                  onChange={(e) => setProfileForm({ ...profileForm, dob: e.target.value })}
                />

                <select
                  className="select"
                  value={profileForm.blood_group}
                  onChange={(e) => setProfileForm({ ...profileForm, blood_group: e.target.value })}
                >
                  <option value="">Blood Group</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                </select>

                <select
                  className="select"
                  value={profileForm.gender}
                  onChange={(e) => setProfileForm({ ...profileForm, gender: e.target.value })}
                >
                  <option value="">Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>

                <input
                  className="input"
                  placeholder="Phone"
                  value={profileForm.phone}
                  onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                />

                <input
                  className="input"
                  placeholder="Address"
                  value={profileForm.address}
                  onChange={(e) => setProfileForm({ ...profileForm, address: e.target.value })}
                />

                <select
                  className="select"
                  value={profileForm.hospital_id}
                  onChange={(e) => setProfileForm({ ...profileForm, hospital_id: e.target.value })}
                >
                  <option value="">Select Hospital</option>
                  {hospitals.map((hospital) => (
                    <option key={hospital.hospital_id} value={hospital.hospital_id}>
                      {hospital.name} - {hospital.address}
                    </option>
                  ))}
                </select>
              </div>

              <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={createProfile}>
                Register Recipient
              </button>
            </div>
          ) : (
            <>
              <div className="card">
                <h2 className="page-title">Recipient Details</h2>
                <div className="details-grid">
                  <div className="detail-box">
                    <span className="detail-label">Name</span>
                    <span className="detail-value">{profile.name}</span>
                  </div>
                  <div className="detail-box">
                    <span className="detail-label">DOB</span>
                    <span className="detail-value">{String(profile.dob).slice(0, 10)}</span>
                  </div>
                  <div className="detail-box">
                    <span className="detail-label">Blood Group</span>
                    <span className="detail-value">{profile.blood_group}</span>
                  </div>
                  <div className="detail-box">
                    <span className="detail-label">Gender</span>
                    <span className="detail-value">{profile.gender || "-"}</span>
                  </div>
                  <div className="detail-box">
                    <span className="detail-label">Phone</span>
                    <span className="detail-value">{profile.phone || "-"}</span>
                  </div>
                  <div className="detail-box">
                    <span className="detail-label">Address</span>
                    <span className="detail-value">{profile.address || "-"}</span>
                  </div>
                  <div className="detail-box detail-box-wide">
                    <span className="detail-label">Hospital ID</span>
                    <span className="detail-value">{profile.hospital_id}</span>
                  </div>
                </div>
              </div>

              <NotificationsPanel />
            </>
          )}
        </div>

        <div className="right-column">
          <div className="card">
            <h2 className="page-title">Create Transplant Request</h2>
            <p className="muted-text">
              You can create multiple requests. You can also edit urgency or delete them below.
            </p>

            <div className="form-grid">
              <select
                className="select"
                value={requestForm.organ_needed}
                onChange={(e) => setRequestForm({ ...requestForm, organ_needed: e.target.value })}
              >
                <option value="">Organ Needed</option>
                {ORGAN_OPTIONS.map((organ) => (
                  <option key={organ} value={organ}>{organ}</option>
                ))}
              </select>

              <select
                className="select"
                value={requestForm.urgency_level}
                onChange={(e) => setRequestForm({ ...requestForm, urgency_level: e.target.value })}
              >
                <option value="">Urgency Level</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>

            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={createRequest}>
              Create Request
            </button>

            {message && <p style={{ marginTop: 14 }} className="success-text">{message}</p>}
          </div>

          <div className="card" style={{ marginTop: 20 }}>
            <h2 className="page-title">My Requests</h2>

            {requests.length === 0 ? (
              <p className="muted-text">No requests created yet.</p>
            ) : (
              <div className="list-box">
                {requests.map((req) => (
                  <div className="request-card" key={req.request_id}>
                    <div className="request-top">
                      <div>
                        <h3 className="request-title">{req.organ_needed}</h3>
                        <p className="muted-text">Requested on: {String(req.requested_on).replace("T", " ").slice(0, 19)}</p>
                      </div>
                      <span className="badge">{req.status}</span>
                    </div>

                    <div className="request-actions">
                      <select
                        className="select"
                        value={req.urgency_level}
                        onChange={(e) => updateUrgency(req.request_id, e.target.value)}
                      >
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                      </select>

                      <button
                        className="btn btn-danger"
                        onClick={() => deleteRequest(req.request_id)}
                      >
                        Delete Request
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default RecipientDashboard;