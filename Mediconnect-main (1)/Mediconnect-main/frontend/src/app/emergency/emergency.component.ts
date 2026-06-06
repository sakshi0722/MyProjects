import {
  Component, OnInit, OnDestroy, AfterViewInit,
  ElementRef, ViewChild, ChangeDetectorRef, NgZone
} from '@angular/core';
import { EmergencyService, Hospital, EmergencyContact } from './emergency.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

declare var L: any;

@Component({
  selector: 'app-emergency',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  providers: [EmergencyService],
  templateUrl: './emergency.component.html',
  styleUrls: ['./emergency.component.scss']
})
export class EmergencyComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('mapContainer') mapContainer!: ElementRef;

  // State
  inputText: string = '';
  isListening: boolean = false;
  isLoading: boolean = false;
  locationStatus: string = '';
  errorMessage: string = '';
  successMessage: string = '';

  // Data
  userLocation: { lat: number; lng: number } | null = null;
  hospitals: Hospital[] = [];
  recommendedHospital: Hospital | null = null;
  selectedHospital: Hospital | null = null;
  emergencyType: string = '';
  contacts: EmergencyContact[] = [];

  // Map
  map: any = null;
  markers: any[] = [];
  userMarker: any = null;
  routeLayer: any = null;

  // Voice
  recognition: any = null;
  userId = 'user_001';

  // Contacts modal
  showContactsModal = false;
  showAddContact = false;
  newContact: EmergencyContact = { name: '', phone: '', relation: '' };

  emergencyIcons: { [key: string]: string } = {
    cardiac: '❤️',
    trauma: '🚑',
    respiratory: '🫁',
    neurological: '🧠',
    burns: '🔥',
    pediatric: '👶',
    general: '🏥'
  };

  constructor(
    private emergencyService: EmergencyService,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  ngOnInit(): void {
    this.detectLocation();
    this.loadContacts();
    this.initVoiceRecognition();
  }

  ngAfterViewInit(): void {
    setTimeout(() => this.initMap(), 300);
  }

  ngOnDestroy(): void {
    if (this.recognition) this.recognition.stop();
    if (this.map) this.map.remove();
  }

  // ─── Location ───────────────────────────────────────────────────────────────

  detectLocation(): void {
    this.locationStatus = 'Detecting your location...';
    if (!navigator.geolocation) {
      this.locationStatus = '';
      this.userLocation = { lat: 18.6298, lng: 73.7997 };
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        this.ngZone.run(() => {
          this.userLocation = { lat: pos.coords.latitude, lng: pos.coords.longitude };
          this.locationStatus = '📍 Location detected';
          setTimeout(() => { this.locationStatus = ''; this.cdr.detectChanges(); }, 3000);
          if (this.map) this.centerMapOnUser();
          this.cdr.detectChanges();
        });
      },
      () => {
        this.ngZone.run(() => {
          this.locationStatus = '';
          this.userLocation = { lat: 18.6298, lng: 73.7997 };
          if (this.map) this.centerMapOnUser();
          this.cdr.detectChanges();
        });
      }
    );
  }

  // ─── Leaflet Map ─────────────────────────────────────────────────────────────

  initMap(): void {
    if (typeof L === 'undefined') {
      console.error('Leaflet not loaded');
      return;
    }
    const center = this.userLocation || { lat: 18.6298, lng: 73.7997 };

    this.map = L.map(this.mapContainer.nativeElement, {
      center: [center.lat, center.lng],
      zoom: 13,
      zoomControl: true
    });

    // OpenStreetMap tile layer — completely free
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19
    }).addTo(this.map);

    if (this.userLocation) this.centerMapOnUser();
  }

  centerMapOnUser(): void {
    if (!this.map || !this.userLocation) return;

    if (this.userMarker) this.map.removeLayer(this.userMarker);

    // Blue circle for user location
    this.userMarker = L.circleMarker(
      [this.userLocation.lat, this.userLocation.lng],
      {
        radius: 10,
        fillColor: '#3b82f6',
        color: '#ffffff',
        weight: 3,
        opacity: 1,
        fillOpacity: 1
      }
    ).addTo(this.map).bindPopup('<b>📍 Your Location</b>');

    this.map.panTo([this.userLocation.lat, this.userLocation.lng]);
  }

  showHospitalsOnMap(): void {
    if (!this.map) return;

    // Remove old markers
    this.markers.forEach(m => this.map.removeLayer(m));
    this.markers = [];

    // Remove old route
    if (this.routeLayer) {
      this.map.removeLayer(this.routeLayer);
      this.routeLayer = null;
    }

    const bounds: any[] = [];
    if (this.userLocation) bounds.push([this.userLocation.lat, this.userLocation.lng]);

    this.hospitals.forEach((h, i) => {
      const isRecommended = h.id === this.recommendedHospital?.id;

      // Red for recommended, blue for others
      const markerColor = isRecommended ? '#dc2626' : '#2563eb';
      const markerSize = isRecommended ? 14 : 10;

      const marker = L.circleMarker(
        [h.latitude, h.longitude],
        {
          radius: markerSize,
          fillColor: markerColor,
          color: '#ffffff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.9
        }
      ).addTo(this.map);

      marker.bindPopup(`
        <div style="font-family:sans-serif;min-width:200px">
          <h3 style="margin:0 0 6px;color:#dc2626;font-size:14px">${h.name}</h3>
          <p style="margin:2px 0;font-size:12px">📍 ${h.address}</p>
          <p style="margin:2px 0;font-size:12px">📞 ${h.phone}</p>
          <p style="margin:2px 0;font-size:12px">🏃 ${h.eta_minutes} min · ${h.distance_km} km</p>
          <p style="margin:2px 0;font-size:12px">🛏 ${h.available_beds} beds available</p>
          ${isRecommended ? '<p style="color:#16a34a;font-weight:700;font-size:12px">⭐ RECOMMENDED</p>' : ''}
        </div>
      `);

      marker.on('click', () => {
        this.ngZone.run(() => this.selectHospital(h));
      });

      this.markers.push(marker);
      bounds.push([h.latitude, h.longitude]);
    });

    // Fit map to show all markers
    if (bounds.length > 1) {
      this.map.fitBounds(bounds, { padding: [40, 40] });
    }

    // Draw straight line route to recommended hospital
    if (this.recommendedHospital && this.userLocation) {
      this.drawRoute(this.recommendedHospital);
    }
  }

  drawRoute(hospital: Hospital): void {
    if (!this.map || !this.userLocation) return;

    if (this.routeLayer) {
      this.map.removeLayer(this.routeLayer);
    }

    // Draw a dashed line from user to hospital
    this.routeLayer = L.polyline(
      [
        [this.userLocation.lat, this.userLocation.lng],
        [hospital.latitude, hospital.longitude]
      ],
      {
        color: '#dc2626',
        weight: 3,
        opacity: 0.8,
        dashArray: '10, 10'
      }
    ).addTo(this.map);
  }

  selectHospital(hospital: Hospital): void {
    this.selectedHospital = hospital;
    this.drawRoute(hospital);

    // Update marker sizes
    this.markers.forEach((m, i) => {
      const isSelected = this.hospitals[i]?.id === hospital.id;
      m.setStyle({
        radius: isSelected ? 14 : 10,
        fillColor: isSelected ? '#dc2626' : '#2563eb'
      });
    });

    this.cdr.detectChanges();
  }

  // ─── Voice ──────────────────────────────────────────────────────────────────

  initVoiceRecognition(): void {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    this.recognition = new SpeechRecognition();
    this.recognition.lang = 'en-IN';
    this.recognition.continuous = false;
    this.recognition.interimResults = false;

    this.recognition.onresult = (event: any) => {
      this.ngZone.run(() => {
        this.inputText = event.results[0][0].transcript;
        this.isListening = false;
        this.cdr.detectChanges();
      });
    };
    this.recognition.onerror = () => {
      this.ngZone.run(() => { this.isListening = false; this.cdr.detectChanges(); });
    };
    this.recognition.onend = () => {
      this.ngZone.run(() => { this.isListening = false; this.cdr.detectChanges(); });
    };
  }

  toggleVoice(): void {
    if (!this.recognition) {
      this.errorMessage = 'Voice not supported in this browser. Please use Chrome.';
      return;
    }
    if (this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    } else {
      this.recognition.start();
      this.isListening = true;
    }
  }

  // ─── Emergency Search ────────────────────────────────────────────────────────

  handleEmergency(): void {
    if (!this.inputText.trim()) {
      this.errorMessage = 'Please describe your emergency (by text or voice).';
      return;
    }
    if (!this.userLocation) {
      this.errorMessage = 'Location not available yet. Please wait...';
      this.detectLocation();
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.hospitals = [];

    this.emergencyService.findHospitals(
      this.userId,
      this.inputText,
      this.userLocation.lat,
      this.userLocation.lng
    ).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          this.hospitals = res.hospitals;
          this.recommendedHospital = res.recommended;
          this.selectedHospital = res.recommended;
          this.emergencyType = res.emergency_type;
          this.isLoading = false;
          this.cdr.detectChanges();
          setTimeout(() => this.showHospitalsOnMap(), 100);
        });
      },
      error: () => {
        this.ngZone.run(() => {
          this.isLoading = false;
          this.errorMessage = 'Could not reach server. Please call 108 immediately.';
          this.cdr.detectChanges();
        });
      }
    });
  }

  callHospital(phone: string): void {
    window.location.href = `tel:${phone}`;
  }

  callContact(phone: string): void {
    window.location.href = `tel:${phone}`;
  }

  // ─── Contacts ────────────────────────────────────────────────────────────────

  loadContacts(): void {
    this.emergencyService.getContacts(this.userId).subscribe({
      next: (res) => { this.contacts = res.contacts; this.cdr.detectChanges(); },
      error: () => {
        this.contacts = [
          { name: 'Ambulance', phone: '108', relation: 'Emergency Services' },
          { name: 'Police', phone: '100', relation: 'Emergency Services' }
        ];
      }
    });
  }

  addContact(): void {
    if (!this.newContact.name || !this.newContact.phone) return;
    const personalContacts = this.contacts.filter(c => c.relation !== 'Emergency Services');
    personalContacts.push({ ...this.newContact });

    this.emergencyService.saveContacts(this.userId, personalContacts).subscribe({
      next: () => {
        this.loadContacts();
        this.newContact = { name: '', phone: '', relation: '' };
        this.showAddContact = false;
        this.successMessage = 'Contact saved!';
        setTimeout(() => { this.successMessage = ''; this.cdr.detectChanges(); }, 3000);
      }
    });
  }

  removeContact(index: number): void {
    const personalContacts = this.contacts.filter(c => c.relation !== 'Emergency Services');
    const offset = this.contacts.length - personalContacts.length;
    const realIndex = index - offset;
    if (realIndex >= 0) {
      personalContacts.splice(realIndex, 1);
      this.emergencyService.saveContacts(this.userId, personalContacts)
        .subscribe(() => this.loadContacts());
    }
  }

  getEmergencyIcon(): string {
    return this.emergencyIcons[this.emergencyType] || '🏥';
  }
}