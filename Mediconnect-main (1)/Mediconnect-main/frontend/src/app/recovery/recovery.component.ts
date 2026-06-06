import {
  Component, OnInit, ChangeDetectorRef, NgZone, ViewChild, ElementRef
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpEventType } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { AuthService } from '../auth/auth.service';

interface MealItem { name: string; quantity: string; calories: number | null; notes: string | null; }
interface DayPlan {
  day: string;
  breakfast: MealItem[];
  mid_morning: MealItem[];
  lunch: MealItem[];
  evening_snack: MealItem[];
  dinner: MealItem[];
  water_intake: string;
}
interface ExerciseItem { name: string; duration: string; sets_reps: string | null; notes: string | null; is_avoid: boolean; }
interface RecoveryResult {
  plan_id: string;
  condition: string;
  patient_info: any;
  report_summary: string;
  diet_plan: DayPlan[];
  exercise_plan: ExerciseItem[];
  foods_to_avoid: string[];
  foods_to_include: string[];
  general_tips: string[];
  follow_up: string;
  source: string;
}

@Component({
  selector: 'app-recovery-page',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './recovery.component.html',
  styleUrls: ['./recovery.component.scss']
})
export class RecoveryPageComponent implements OnInit {
  @ViewChild('reportInput') reportInput!: ElementRef;

  // Steps: 1=Personal Info, 2=Injury & Health, 3=Lifestyle, 4=Report Upload
  currentStep: number = 1;
  isGenerating: boolean = false;
  uploadProgress: number = 0;
  result: RecoveryResult | null = null;
  errorMessage: string = '';

  // Active tabs in result
  activeDietDay: number = 0;
  activeResultTab: string = 'diet';

  // Form fields
  form = {
    user_id: 'user_001',
    name: '',
    age: null as number | null,
    gender: '',
    weight_kg: null as number | null,
    height_cm: null as number | null,
    injury_type: '',           // NEW — specific injury/surgery
    injury_date: '',           // NEW — when did it happen
    recovery_goal: '',
    food_preference: '',
    activity_level: '',
    allergies: '',
    health_conditions: '',
    current_medications: '',
  };

  // Report upload
  reportFile: File | null = null;
  reportPreview: string | null = null;
  isDragging: boolean = false;

  // Predefined options
  healthConditionOptions = [
    'Diabetes', 'Hypertension (High BP)', 'Heart Disease',
    'Thyroid', 'Kidney Disease', 'Arthritis', 'Anaemia', 'Obesity'
  ];
  selectedConditions: string[] = [];

  injuryOptions = [
    'Knee Surgery / Replacement',
    'Hip Surgery / Replacement',
    'Appendix / Abdominal Surgery',
    'Fracture / Broken Bone',
    'Back / Spine Injury',
    'Heart Surgery / Bypass',
    'Road Accident Injuries',
    'Sports Injury',
    'Burn Injury',
    'Post Delivery / C-Section',
    'Dengue / Typhoid Recovery',
    'Covid Recovery',
    'Other',
  ];

  private apiUrl = environment.apiUrl;

  constructor(
    private http: HttpClient,
    private auth: AuthService,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  ngOnInit(): void {
    this.form.user_id = this.auth.userId;
  }

  // ─── Steps Navigation ────────────────────────────────────────────────────

  nextStep(): void {
    if (this.currentStep === 1 && !this.validateStep1()) return;
    if (this.currentStep === 2 && !this.validateStep2()) return;
    if (this.currentStep === 3 && !this.validateStep3()) return;
    this.currentStep++;
    this.errorMessage = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  prevStep(): void {
    this.currentStep--;
    this.errorMessage = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  validateStep1(): boolean {
    if (!this.form.name.trim()) { this.errorMessage = 'Please enter your name.'; return false; }
    if (!this.form.age || this.form.age < 1) { this.errorMessage = 'Please enter a valid age.'; return false; }
    if (!this.form.gender) { this.errorMessage = 'Please select your gender.'; return false; }
    if (!this.form.weight_kg || this.form.weight_kg < 1) { this.errorMessage = 'Please enter your weight.'; return false; }
    if (!this.form.height_cm || this.form.height_cm < 1) { this.errorMessage = 'Please enter your height.'; return false; }
    return true;
  }

  validateStep2(): boolean {
    if (!this.form.injury_type) { this.errorMessage = 'Please select or describe your injury/condition.'; return false; }
    return true;
  }

  validateStep3(): boolean {
    if (!this.form.food_preference) { this.errorMessage = 'Please select your food preference.'; return false; }
    if (!this.form.activity_level) { this.errorMessage = 'Please select your activity level.'; return false; }
    return true;
  }

  selectInjury(injury: string): void {
    this.form.injury_type = injury;
    // Auto-fill recovery goal if not already set
    if (!this.form.recovery_goal) {
      this.form.recovery_goal = `Recovering from ${injury}`;
    }
  }

  toggleCondition(condition: string): void {
    const idx = this.selectedConditions.indexOf(condition);
    if (idx > -1) {
      this.selectedConditions.splice(idx, 1);
    } else {
      this.selectedConditions.push(condition);
    }
    this.form.health_conditions = this.selectedConditions.join(', ');
  }

  isConditionSelected(condition: string): boolean {
    return this.selectedConditions.includes(condition);
  }

  // ─── Report Upload ────────────────────────────────────────────────────────

  onReportSelected(event: any): void {
    const file = event.target.files[0];
    if (file) this.processReport(file);
  }

  onDragOver(e: DragEvent): void { e.preventDefault(); this.isDragging = true; }
  onDragLeave(e: DragEvent): void { this.isDragging = false; }
  onDrop(e: DragEvent): void {
    e.preventDefault(); this.isDragging = false;
    const file = e.dataTransfer?.files[0];
    if (file) this.processReport(file);
  }

  processReport(file: File): void {
    const allowed = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/pdf'];
    if (!allowed.includes(file.type)) {
      this.errorMessage = 'Please upload JPEG, PNG, or PDF file.';
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      this.errorMessage = 'File too large. Max 10MB.';
      return;
    }
    this.reportFile = file;
    this.errorMessage = '';
    if (file.type !== 'application/pdf') {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.ngZone.run(() => {
          this.reportPreview = e.target?.result as string;
          this.cdr.detectChanges();
        });
      };
      reader.readAsDataURL(file);
    } else {
      this.reportPreview = 'pdf';
    }
  }

  clearReport(): void {
    this.reportFile = null;
    this.reportPreview = null;
    if (this.reportInput) this.reportInput.nativeElement.value = '';
  }

  // ─── Generate Plan ────────────────────────────────────────────────────────

  generatePlan(): void {
    this.isGenerating = true;
    this.uploadProgress = 0;
    this.errorMessage = '';

    // Build recovery_goal from injury + goal
    if (!this.form.recovery_goal && this.form.injury_type) {
      this.form.recovery_goal = `Recovering from ${this.form.injury_type}`;
    }

    const formData = new FormData();
    Object.entries(this.form).forEach(([k, v]) => {
      if (v !== null && v !== undefined) formData.append(k, String(v));
    });
    if (this.reportFile) formData.append('report', this.reportFile);

    this.http.post<RecoveryResult>(
      `${this.apiUrl}/api/recovery/generate-plan`,
      formData,
      { reportProgress: true, observe: 'events' }
    ).subscribe({
      next: (event) => {
        this.ngZone.run(() => {
          if (event.type === HttpEventType.UploadProgress && event.total) {
            this.uploadProgress = Math.round(100 * event.loaded / event.total);
          } else if (event.type === HttpEventType.Response) {
            this.result = event.body as RecoveryResult;
            this.isGenerating = false;
            this.activeDietDay = 0;
            this.activeResultTab = 'diet';
            this.cdr.detectChanges();
            setTimeout(() => {
              document.querySelector('.result-section')?.scrollIntoView({ behavior: 'smooth' });
            }, 100);
          }
          this.cdr.detectChanges();
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          this.isGenerating = false;
          this.errorMessage = err.error?.detail || 'Failed to generate plan. Please try again.';
          this.cdr.detectChanges();
        });
      }
    });
  }

  // ─── Helpers ─────────────────────────────────────────────────────────────

  getBMI(): string {
    if (!this.form.weight_kg || !this.form.height_cm) return '';
    const h = this.form.height_cm / 100;
    return (this.form.weight_kg / (h * h)).toFixed(1);
  }

  getBMILabel(): string {
    const bmi = +this.getBMI();
    if (!bmi) return '';
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
  }

  getDayShort(day: string): string {
    return day.split('–')[0]?.trim() || day;
  }

  getMealCalories(meals: MealItem[]): number {
    return meals.reduce((sum, m) => sum + (m.calories || 0), 0);
  }

  getTotalCalories(day: DayPlan): number {
    return this.getMealCalories(day.breakfast) +
      this.getMealCalories(day.mid_morning) +
      this.getMealCalories(day.lunch) +
      this.getMealCalories(day.evening_snack) +
      this.getMealCalories(day.dinner);
  }

  startOver(): void {
    this.result = null;
    this.currentStep = 1;
    this.reportFile = null;
    this.reportPreview = null;
    this.errorMessage = '';
    this.selectedConditions = [];
    this.form = {
      user_id: this.auth.userId, name: '', age: null, gender: '',
      weight_kg: null, height_cm: null,
      injury_type: '', injury_date: '', recovery_goal: '',
      food_preference: '', activity_level: '',
      allergies: '', health_conditions: '', current_medications: ''
    };
  }
}