import {
  Component, OnInit, ChangeDetectorRef, NgZone, ElementRef, ViewChild
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpEventType } from '@angular/common/http';
import { AuthService } from '../auth/auth.service';
import { environment } from '../../environments/environment';

interface FirstAidStep {
  step_number: number;
  instruction: string;
  is_critical: boolean;
}

interface InjuryResult {
  injury_type: string;
  severity: string;
  confidence: number;
  first_aid_steps: FirstAidStep[];
  do_list: string[];
  dont_list: string[];
  seek_doctor: boolean;
  seek_doctor_reason: string;
  estimated_healing: string;
  warning_signs: string[];
  source: string;
}

@Component({
  selector: 'app-minor-injury',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './minor-injury.component.html',
  styleUrls: ['./minor-injury.component.scss']
})
export class MinorInjuryComponent implements OnInit {
  @ViewChild('fileInput') fileInput!: ElementRef;

  // Upload state
  selectedFile: File | null = null;
  previewUrl: string | null = null;
  description: string = '';
  isDragging: boolean = false;

  // Analysis state
  isAnalyzing: boolean = false;
  uploadProgress: number = 0;
  result: InjuryResult | null = null;
  errorMessage: string = '';

  // UI state
  activeTab: string = 'steps'; // steps | dos | warnings
  userId: string = 'user_001'; // will be set in ngOnInit

  private apiUrl = environment.apiUrl;

  constructor(
    private http: HttpClient,
    private auth: AuthService,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  ngOnInit(): void {
    this.userId = this.auth.userId;
  }

  // ─── File Handling ────────────────────────────────────────────────────────

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) this.processFile(file);
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent): void {
    this.isDragging = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;
    const file = event.dataTransfer?.files[0];
    if (file) this.processFile(file);
  }

  processFile(file: File): void {
    const allowed = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowed.includes(file.type)) {
      this.errorMessage = 'Please upload a JPEG, PNG, or WebP image.';
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      this.errorMessage = 'Image too large. Max size is 5MB.';
      return;
    }

    this.selectedFile = file;
    this.errorMessage = '';
    this.result = null;

    const reader = new FileReader();
    reader.onload = (e) => {
      this.ngZone.run(() => {
        this.previewUrl = e.target?.result as string;
        this.cdr.detectChanges();
      });
    };
    reader.readAsDataURL(file);
  }

  clearImage(): void {
    this.selectedFile = null;
    this.previewUrl = null;
    this.result = null;
    this.errorMessage = '';
    this.description = '';
    if (this.fileInput) this.fileInput.nativeElement.value = '';
  }

  // ─── Analysis ────────────────────────────────────────────────────────────

  analyzeInjury(): void {
    if (!this.selectedFile) {
      this.errorMessage = 'Please upload an image of the injury first.';
      return;
    }

    this.isAnalyzing = true;
    this.uploadProgress = 0;
    this.errorMessage = '';
    this.result = null;

    const formData = new FormData();
    formData.append('image', this.selectedFile);
    formData.append('user_id', this.userId);
    formData.append('description', this.description);

    this.http.post<InjuryResult>(
      `${this.apiUrl}/api/minor-injury/analyze`,
      formData,
      { reportProgress: true, observe: 'events' }
    ).subscribe({
      next: (event) => {
        this.ngZone.run(() => {
          if (event.type === HttpEventType.UploadProgress && event.total) {
            this.uploadProgress = Math.round(100 * event.loaded / event.total);
          } else if (event.type === HttpEventType.Response) {
            this.result = event.body as InjuryResult;
            this.isAnalyzing = false;
            this.activeTab = 'steps';
            this.cdr.detectChanges();
            // Scroll to results
            setTimeout(() => {
              document.querySelector('.results-section')?.scrollIntoView({ behavior: 'smooth' });
            }, 100);
          }
          this.cdr.detectChanges();
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          this.isAnalyzing = false;
          this.errorMessage = err.error?.detail || 'Analysis failed. Please try again.';
          this.cdr.detectChanges();
        });
      }
    });
  }

  // ─── Helpers ─────────────────────────────────────────────────────────────

  getSeverityColor(): string {
    switch (this.result?.severity) {
      case 'mild': return 'green';
      case 'moderate': return 'orange';
      case 'severe': return 'red';
      default: return 'gray';
    }
  }

  getSeverityIcon(): string {
    switch (this.result?.severity) {
      case 'mild': return '🟢';
      case 'moderate': return '🟡';
      case 'severe': return '🔴';
      default: return '⚪';
    }
  }

  getConfidencePercent(): number {
    return Math.round((this.result?.confidence || 0) * 100);
  }
}