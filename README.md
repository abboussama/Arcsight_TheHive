# **Arcsight_TheHive Integration**

Integrate ArcSight with TheHive seamlessly, without using the ArcSight API. This solution only requires an ESM account to push alerts to TheHive.

---

## **Project Structure**
- **`arcsight_alerts/`**: The starting point of the integration process.
- **`main.py`**: The script responsible for pushing alerts to TheHive.
- **`getAlerts.py`**: Handles data cleaning, separation, and normalization before sending the data to TheHive API.

---

## **Setup Instructions**

Before running the script, ensure the following data is configured:

### **1. ArcSight ESM Configuration**
- ESM **username**
- ESM **password**
- ESM **hostname**

### **2. TheHive Configuration**
- TheHive **API key** (with appropriate privileges)
- TheHive **hostname**

---

## **Optional Settings**
- **SSL Certificates**:  
  If you want to use SSL certificates with TheHive API, set `useSSL` to `True` in the script.
- **Custom Parameters**:  
  Customize other parameters as needed, such as:
  - `tenant_name`
  - `client_name`
  - Any additional settings specific to your environment.

---

## **How It Works**
1. Alerts are retrieved from ArcSight using the provided ESM credentials.
2. The `getAlerts` module processes and normalizes the data.
3. Alerts are pushed to TheHive via its API for further analysis and triage.

---

Feel free to raise an issue or submit a pull request for any improvements or bug fixes! 
