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

function DonorDashboard() {
  const user = JSON.parse(localStorage.getItem("user"));

  const [profile, setProfile] = useState(null);
  const [hospitals, setHospitals] = useState([]);
  const [message, setMessage] = useState("");

  const [profileForm, setProfileForm] = useState({
    name: "",
    dob: "",
    blood_group: "",
    gender: "",
    phone: "",
    address: "",
    condition: "",
    hospital_id: ""
  });

  const [organForm, setOrganForm] = useState({
    type: "",
    blood_group: "",
    status: "Available"
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
      const res = await API.get(`/donors/profile/${user.user_id}`);
      setProfile(res.data);
      setOrganForm((prev) => ({
        ...prev,
        blood_group: res.data.blood_group || ""
      }));
    } catch {
      setProfile(null);
    }
  };

  useEffect(() => {
    loadHospitals();
    loadProfile();
  }, []);

  const createProfile = async () => {
    try {
      const res = await API.post("/donors/profile", {
        ...profileForm,
        user_id: user.user_id
      });
      setMessage(res.data.message || "Donor profile created successfully");
      loadProfile();
    } catch (err) {
      setMessage(err?.response?.data?.error || "Failed to create donor profile");
    }
  };

  const addOrgan = async () => {
    try {
      if (!profile) {
        setMessage("Please complete donor registration first");
        return;
      }

      const res = await API.post("/organs", {
        ...organForm,
        donor_id: profile.donor_id,
        hospital_id: profile.hospital_id,
        blood_group: profile.blood_group
      });

      setMessage(res.data.message || "Organ added successfully");
      setOrganForm({
        type: "",
        blood_group: profile.blood_group || "",
        status: "Available"
      });
    } catch (err) {
      setMessage(err?.response?.data?.error || "Failed to add organ");
    }
  };

  return (
    <div className="page-container">
      <Navbar />

      <div className="recipient-layout">
        <div className="left-column">
          {!profile ? (
            <div className="card">
              <h2 className="page-title">Donor Registration</h2>
              <p className="muted-text">
                Register once. After that, your details will appear here and you can add organs for donation.
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
                  value={profileForm.condition}
                  onChange={(e) => setProfileForm({ ...profileForm, condition: e.target.value })}
                >
                  <option value="">Condition</option>
                  <option value="Healthy">Healthy</option>
                  <option value="Deceased">Deceased</option>
                  <option value="Dead">Dead</option>
                </select>

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
                Register Donor
              </button>
            </div>
          ) : (
            <>
              <div className="card">
                <h2 className="page-title">Donor Details</h2>
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
                  <div className="detail-box">
                    <span className="detail-label">Condition</span>
                    <span className="detail-value">{profile.donor_condition}</span>
                  </div>
                  <div className="detail-box">
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
            <h2 className="page-title">Add Organs for Donation</h2>
            <p className="muted-text">
              You can add multiple organs one by one. Recipients will be notified when a new organ is added.
            </p>

            <div className="form-grid">
              <select
                className="select"
                value={organForm.type}
                onChange={(e) => setOrganForm({ ...organForm, type: e.target.value })}
              >
                <option value="">Select Organ</option>
                {ORGAN_OPTIONS.map((organ) => (
                  <option key={organ} value={organ}>{organ}</option>
                ))}
              </select>

              <input
                className="input"
                value={profile?.blood_group || ""}
                readOnly
                placeholder="Blood Group"
              />

              <select
                className="select"
                value={organForm.status}
                onChange={(e) => setOrganForm({ ...organForm, status: e.target.value })}
              >
                <option value="Available">Available</option>
                <option value="Reserved">Reserved</option>
                <option value="Used">Used</option>
              </select>
            </div>

            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={addOrgan}>
              Add Organ
            </button>

            {message && <p style={{ marginTop: 14 }} className="success-text">{message}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DonorDashboard;