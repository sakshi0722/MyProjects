import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Hospital {
  id: string;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  phone: string;
  specialties: string[];
  rating: number;
  available_beds: number;
  distance_km: number;
  eta_minutes: number;
  is_specialized: boolean;
}

export interface EmergencyResponse {
  emergency_type: string;
  user_location: { lat: number; lng: number };
  hospitals: Hospital[];
  recommended: Hospital;
}

export interface EmergencyContact {
  name: string;
  phone: string;
  relation: string;
}

@Injectable({ providedIn: 'root' })
export class EmergencyService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  findHospitals(
    userId: string,
    text: string,
    lat: number,
    lng: number
  ): Observable<EmergencyResponse> {
    return this.http.post<EmergencyResponse>(`${this.apiUrl}/api/emergency/find-hospitals`, {
      user_id: userId,
      input_text: text,
      latitude: lat,
      longitude: lng
    });
  }

  getContacts(userId: string): Observable<{ contacts: EmergencyContact[] }> {
    return this.http.get<{ contacts: EmergencyContact[] }>(
      `${this.apiUrl}/api/emergency/contacts/${userId}`
    );
  }

  saveContacts(userId: string, contacts: EmergencyContact[]): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/emergency/contacts`, {
      user_id: userId,
      contacts
    });
  }
}
