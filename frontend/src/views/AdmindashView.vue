<template>
  <div class="lot-table-container">
    <h2>Parking Lots</h2>
    <div class="button-group">
      <button class="create-btn" @click="openCreateForm">Create New Lot</button>
      <button class="users-btn" @click="fetchAllUsers">View All Users</button>
    </div>
    <table class="lot-table">
      <thead>
        <tr>
          <th>Lot</th>
          <th>Capacity</th>
          <th>Available Spots</th>
          <th>Occupied Spots</th>
          <th>Area</th>
          <th>Price (₹)</th>
          <th>Spot Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lot in parkingLots" :key="lot.lot">
          <td>Parking#{{ lot.lot }}</td>
          <td>{{ lot.capacity }}</td>
          <td>{{ lot.available }}</td>
          <td>{{ lot.capacity - lot.available }}</td>
          <td>{{ lot.area }}</td>
          <td>{{ lot.price }}</td>
          <td>
            <div class="spot-status">
              <span
                v-for="spot in lot.spots"
                :key="spot.id"
                class="spot-box"
                :class="{ 'available': spot.status === 'A', 'occupied': spot.status === 'O' }"
                :title="spot.status === 'A' ? 'Available' : 'Occupied'"
                @click="fetchSpotDetails(lot, spot.id)"
              ></span>

            </div>
          </td>
          <td>
            <button class="edit-btn" @click="openEditForm(lot)">Edit</button>
            <button class="delete-btn" @click="deleteLot(lot.lot)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="showEditModal" class="modal">
    <div class="modal-content">
      <h3>Edit Lot #{{ editingLot.lot }}</h3>
      <label>Area:</label>
      <input v-model="editingLot.area" />
      <label>Pin Code:</label>
      <input v-model="editingLot.pin_code" />
      <label>Price:</label>
      <input type="number" v-model="editingLot.price" />
      <label>Capacity:</label>
      <input type="number" v-model.number="editingLot.capacity" @input="onCapacityChange" />
      <div class="modal-actions">
        <button @click="submitEditForm">Save</button>
        <button @click="showEditModal = false">Cancel</button>
      </div>
    </div>
  </div>

  <div v-if="showCreateModal" class="modal">
    <div class="modal-content">
      <h3>Create New Lot</h3>
      <label>Lot ID:</label>
      <input v-model.number="newLot.l_id" placeholder="Enter Lot ID" />
      <label>Area:</label>
      <input v-model="newLot.area" placeholder="Enter Area" />
      <label>Pin Code:</label>
      <input v-model="newLot.pin" placeholder="Enter Pin Code" />
      <label>Price:</label>
      <input type="number" v-model.number="newLot.price" placeholder="Enter Price" />
      <label>Address:</label>
      <input v-model="newLot.address" placeholder="Enter Address" />
      <label>Number of Spots:</label>
      <input type="number" v-model.number="newLot.available" placeholder="Enter Number of Spots" />
      <div class="modal-actions">
        <button @click="submitCreateForm">Create</button>
        <button @click="showCreateModal = false">Cancel</button>
      </div>
    </div>
  </div>

  <div v-if="showSpotDetailsModal" class="modal">
  <div class="modal-content">
    <h3>Spot Details - Lot #{{ selectedLot?.lot }}, Spot #{{ selectedSpot }}</h3>
    <p v-if="spotDetails?.status === 'A'">This spot is free.</p>
    <div v-else-if="spotDetails?.status === 'O'">
      <p><strong>User Details:</strong></p>
      <p>Name: {{ spotDetails.user?.name || 'N/A' }}</p>
      <p>Email: {{ spotDetails.user?.email || 'N/A' }}</p>
      <p>Vehicle Number: {{ spotDetails.user?.vehicle_number || 'N/A' }}</p>
      <p>Parking Time: {{ spotDetails.parking_time || 'N/A' }}</p>
    </div>
    <p v-else>Error: {{ spotError || 'Unable to load spot details' }}</p>
    <div class="modal-actions">
      <button @click="closeSpotDetailsModal">Close</button>
    </div>
  </div>
</div>

  <div v-if="showUsersModal" class="modal">
    <div class="modal-content">
      <h3>All Users</h3>
      <table class="users-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Vehicle Number</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.email">
            <td>{{ user.name || 'N/A' }}</td>
            <td>{{ user.email || 'N/A' }}</td>
            <td>{{ user.vehicleno || 'N/A' }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="usersError">Error: {{ usersError }}</p>
      <div class="modal-actions">
        <button @click="closeUsersModal">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdmindashView',
  data() {
    return {
      parkingLots: [],
      showEditModal: false,
      editingLot: null,
      showCreateModal: false,
      newLot: {
        l_id: null,
        area: '',
        pin: '',
        price: null,
        address: '',
        available: null,
      },
      showSpotDetailsModal: false,
      selectedLot: null,
      selectedSpot: null,
      spotDetails: null,
      spotError: null,
      showUsersModal: false,
      users: [],
      usersError: null,
    };
  },
  mounted() {
    this.fetchParkingLots();
  },
  methods: {
    async fetchParkingLots() {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No token found in localStorage');
        }
        console.log('Fetching lots with token:', token.substring(0, 10) + '...');
        const res = await fetch('http://127.0.0.1:5000/lots', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(`HTTP error! Status: ${res.status}, Message: ${errorData.msg || 'Unknown error'}`);
        }
        const data = await res.json();
        console.log('Raw data:', data);
        this.parkingLots = data['parking lots'].map(lot => ({
          ...lot,
          occupied: lot.capacity - lot.available,
        }));
      } catch (err) {
        console.error('Fetch error:', err);
        alert(`Failed to fetch parking lots: ${err.message}`);
      }
    },
    async fetchSpotDetails(lot, spotId) {
  try {
    console.log(`Clicked on spot #${spotId} in lot #${lot.lot}`);
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No token found in localStorage');
    }
    console.log(`Fetching spot details for lot ${lot.lot}, spot ${spotId}`);
    const res = await fetch(`http://127.0.0.1:5000/lots/${lot.lot}/${spotId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(`HTTP error! Status: ${res.status}, Message: ${errorData.msg || 'Unknown error'}`);
    }
    const data = await res.json();
    console.log('Spot data:', data);
    this.spotDetails = data.spot;
    this.spotError = null;
    this.selectedLot = lot;
    this.selectedSpot = spotId;
    this.showSpotDetailsModal = true;
  } catch (err) {
    console.error('Spot fetch error:', err);
    this.spotError = err.message;
    this.spotDetails = null;
    this.selectedLot = lot;
    this.selectedSpot = spotId;
    this.showSpotDetailsModal = true;
  }
},
    closeSpotDetailsModal() {
      this.showSpotDetailsModal = false;
      this.spotDetails = null;
      this.spotError = null;
      this.selectedLot = null;
      this.selectedSpot = null;
    },
    async fetchAllUsers() {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No token found in localStorage');
        }
        console.log('Fetching all users with token:', token.substring(0, 10) + '...');
        const res = await fetch('http://127.0.0.1:5000/users', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(`HTTP error! Status: ${res.status}, Message: ${errorData.msg || 'Unknown error'}`);
        }
        const data = await res.json();
        console.log('Users data:', data);
        if (data.msg === 'all users') {
          this.users = data.users;
          this.usersError = null;
          this.showUsersModal = true;
        } else {
          throw new Error('Unexpected response format');
        }
      } catch (err) {
        console.error('Users fetch error:', err);
        this.usersError = err.message;
        this.users = [];
        this.showUsersModal = true;
      }
    },
    closeUsersModal() {
      this.showUsersModal = false;
      this.users = [];
      this.usersError = null;
    },
    openEditForm(lot) {
      console.log('Opening edit form for lot:', lot);
      this.editingLot = { ...lot };
      console.log('editingLot initialized:', this.editingLot);
      this.showEditModal = true;
    },
    onCapacityChange(event) {
      const newValue = parseInt(event.target.value, 10);
      console.log('Capacity input changed to:', newValue);
      // Force update to ensure reactivity
      this.editingLot.capacity = newValue;
    },
    async submitEditForm() {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No token found in localStorage');
        }
        console.log('Submitting edit for lot:', this.editingLot);
        const res = await fetch(`http://127.0.0.1:5000/lots/${this.editingLot.lot}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            area: this.editingLot.area,
            price: this.editingLot.price,
            address: this.editingLot.address,
            pin_code: this.editingLot.pin_code,
            capacity: this.editingLot.capacity
          }),
        });
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(`Update failed: ${errorData.msg || 'Unknown error'}`);
        }
        this.showEditModal = false;
        this.editingLot = null;
        await this.fetchParkingLots();
      } catch (err) {
        console.error('Update error:', err);
        alert(`Update failed: ${err.message}`);
      }
    },
    openCreateForm() {
      console.log('Opening create form');
      this.newLot = {
        l_id: null,
        area: '',
        pin: '',
        price: null,
        address: '',
        available: null,
      };
      this.showCreateModal = true;
    },
    async submitCreateForm() {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No token found in localStorage');
        }
        console.log('Submitting new lot:', this.newLot);
        const res = await fetch('http://127.0.0.1:5000/lots', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            l_id: this.newLot.l_id,
            area: this.newLot.area,
            price: this.newLot.price,
            address: this.newLot.address,
            pin: this.newLot.pin,
            available: this.newLot.available,
          }),
        });
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(`Creation failed: ${errorData.error || errorData.msg || 'Unknown error'}`);
        }
        const data = await res.json();
        console.log('Creation response:', data);
        this.showCreateModal = false;
        this.newLot = {
          l_id: null,
          area: '',
          pin: '',
          price: null,
          address: '',
          available: null,
        };
        await this.fetchParkingLots();
      } catch (err) {
        console.error('Creation error:', err);
        alert(`Creation failed: ${err.message}`);
      }
    },
    async deleteLot(lotId) {
      if (!confirm(`Delete Parking Lot #${lotId}?`)) return;

      try {
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No token found in localStorage');
        }
        console.log('Sending DELETE request for lotId:', lotId, 'with token:', token.substring(0, 10) + '...');
        const res = await fetch(`http://127.0.0.1:5000/lots/${lotId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(`Delete failed: Status: ${res.status}, Message: ${errorData.msg || 'Unknown error'}`);
        }
        console.log('Delete successful, refreshing lots');
        await this.fetchParkingLots();
      } catch (err) {
        console.error('Delete error:', err);
        alert(`Delete failed: ${err.message}`);
      }
    },
  },
}
</script>

<style scoped>
.lot-table-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.lot-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.lot-table th,
.lot-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.lot-table th {
  background-color: #03C03C;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.users-table th,
.users-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.users-table th {
  background-color: #2196F3;
}

.edit-btn,
.delete-btn,
.create-btn,
.users-btn {
  padding: 5px 10px;
  margin-right: 5px;
  cursor: pointer;
  border: none;
  color: white;
}

.create-btn {
  background-color: #2196F3;
}

.users-btn {
  background-color: #FFC107;
}

.edit-btn {
  background-color: #4CAF50;
}

.delete-btn {
  background-color: #f44336;
}

.spot-status {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.spot-box {
  width: 16px;
  height: 16px;
  border: 1px solid #ccc;
  border-radius: 3px;
  cursor: pointer;
}

.spot-box.available {
  background-color: #4CAF50;
}

.spot-box.occupied {
  background-color: #f44336;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 12px;
  min-width: 300px;
}

.modal-content label {
  display: block;
  margin: 10px 0 5px;
}

.modal-content input {
  width: 100%;
  padding: 6px;
  margin: 6px 0 12px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>