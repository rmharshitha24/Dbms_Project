import { useEffect, useState } from "react";
import API from "../services/api";

function NotificationsPanel() {
  const [notifications, setNotifications] = useState([]);
  const user = JSON.parse(localStorage.getItem("user"));

  useEffect(() => {
    if (!user?.user_id) return;

    const fetchNotifications = async () => {
      try {
        const res = await API.get(`/notifications/${user.user_id}`);
        setNotifications(res.data || []);
      } catch {
        setNotifications([]);
      }
    };

    fetchNotifications();
  }, [user?.user_id]);

  return (
    <div className="card notifications-box">
      <h3 className="section-title">Notifications</h3>

      {notifications.length > 0 ? (
        <div className="list-box">
          {notifications.map((n, i) => (
            <div className="notification-item" key={n.notification_id || i}>
              <div className="notification-dot" />
              <div>
                <p className="notification-text">{n.message}</p>
                {n.created_at && (
                  <p className="muted-text">
                    {String(n.created_at).replace("T", " ").slice(0, 19)}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="muted-text">No notifications available.</p>
      )}
    </div>
  );
}

export default NotificationsPanel;