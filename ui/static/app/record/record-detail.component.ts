import { Component, ViewChild, OnInit } from "@angular/core";
import {
  Control,
  ControlGroup,
  FormBuilder,
  FORM_DIRECTIVES,
  Validators
} from "@angular/common";
import { CanActivate, Router, RouteParams } from "@angular/router-deprecated";
import { HTTP_PROVIDERS } from "@angular/http";
import { AuthService } from "../auth/auth.service";
import { TooltipDirective } from "../tooltip.directive";
import { AutocompleteComponent } from "../autocomplete/autocomplete.component";
import { Domain } from "../domain/domain";
import { DomainService } from "../domain/domain.service";
import { RecordService } from "./record.service";
import { Record } from "./record";
import { isLoggedin }  from "../auth/auth.service";
import "rxjs/add/observable/throw";


@Component({
  templateUrl: "/static/app/record/record-detail.component.html",
  providers: [HTTP_PROVIDERS, RecordService, DomainService],
  directives: [FORM_DIRECTIVES, AutocompleteComponent, TooltipDirective],
  styles: [`
    .ng-invalid { border-color:#ebccd1;}
    .type-help-text { color:silver;font-size:13px; }
  `]
})
@CanActivate(() => isLoggedin())
export class RecordDetailComponent implements OnInit {

    record: Record;
    domain: Domain;
    errorMessage: any;
    isCreate: boolean = true;
    recordTypes: Array<{0: string, 1: string}> = Record.recordTypes;
    recordForm: ControlGroup;
    saved: boolean = false;
    domainDot: string = "";
    recordName: string = "";
    backUrlParams: {[key: string]: string} = {};
    @ViewChild("inputContent") inputContent;

    constructor(
      private router: Router,
      private routeParams: RouteParams,
      private recordService: RecordService,
      private domainService: DomainService,
      private authService: AuthService,
      private formBuilder: FormBuilder
    ) {
      this.recordForm = formBuilder.group({
        name: [],
        content: ["", Validators.required],
        type: ["", Validators.required],
        ttl: ["", Validators.required],
        prio: [], // Visible only if type is MX
        remarks: []
      });
    }

    ngOnInit() {
      let backUrl: string = this.routeParams.get("backUrl");
      if (backUrl && backUrl.length > 0) {
        this.backUrlParams = JSON.parse(backUrl);
      }
      let recordId: any = this.routeParams.get("id");
      if (!recordId) {
        this.record = new Record();
        this.record.owner = this.authService.getUsername();
        this.isCreate = true;
      } else {
        this.isCreate = false;
        this.recordService.getRecordById(
          String(recordId)
        ).subscribe(
          record => {
            this.record = record;
            this.getDomain();
          },
          error => this.errorMessage = <any>error
        );
      }
    }

    getDomain() {
      if (this.record.domain) {
        this.domainService.getDomainById(
          this.record.domain
        ).subscribe(
          (domain) => {
            this.domain = domain;
            this.setRecordName();
          }
        );
      }
    }

    setApiValidationErrors(errors: Object) {
      for (let fieldName in errors) {
        try {
          this.recordForm.controls[fieldName].setErrors(
            {"apiError": errors[fieldName]}, true
          );
        } catch (TypeError) {
          this.errorMessage = errors[fieldName];
        }
      }
    }

    onSubmit() {
      if (this.recordForm.valid && this.domain) {
        this.saved = true;
        if (this.recordName) {
          let dot: string = this.recordName.endsWith(".") ? "" : ".";
          this.record.name = `${this.recordName}${dot}${this.domain.name}`;
        } else {
          this.record.name = this.domain.name;
        }

        this.recordService.updateOrCreateRecord(this.record).subscribe(
          record => {
            if (record.owner !== this.authService.getUsername()) {
              this.router.navigate(["RecordRequests"]);
            } else {
              this.onBack();
            }
          },
          error => {
            if (typeof error === "string") {
              this.errorMessage = error;
            } else if (error.hasOwnProperty("record_request_ids")) {
              this.router.navigate(["RecordRequests"]);
            } else {
              this.setApiValidationErrors(error);
            }
            this.saved = false;
          }
        );
      }
    }

    setDotDomain() {
      if (this.recordName.length > 0) {
        this.domainDot = ".";
      } else {
        this.domainDot = "";
      }
    }

    onKeyUpName(value: string) {
      this.setDotDomain();
    }

    setRecordName() {
      if (this.record && this.domain && this.record.name) {
        if (this.record.name.endsWith(this.domain.name)) {
          this.recordName = this.record.name.slice(
            0, this.record.name.lastIndexOf(this.domain.name)
          );
          if (this.recordName.endsWith(".")) {
            this.recordName = this.recordName.slice(0, -1);
          }
        } else {
          this.recordName = this.record.name;
        }
      }
      this.setDotDomain();
    }

    get onDomainSelectForAutocomplete() {
      return () => {
        if (this.isCreate) {
          this.record.type = "A";
        }
        this.getDomain();
      };
    }

    get onDomainRemoveForAutocomplete() {
      return () => {
        this.domain = null;
      };
    }

    onChangeType() {
      if (this.isCreate) {
        if (this.record.type === "A" || this.record.type === "MX") {
          this.inputContent.nativeElement.placeholder = "1.2.3.4";
        } else if (this.record.type === "CNAME") {
          this.inputContent.nativeElement.placeholder = "example.com";
        } else if (this.record.type === "TXT") {
          this.inputContent.nativeElement.placeholder = "description here";
        } else if (this.record.type === "SRV") {
          this.inputContent.nativeElement.placeholder = "0 5222 jabber.example.com";
        } else {
          this.inputContent.nativeElement.placeholder = "";
        }
      }
    }

    onBack() {
      if (this.backUrlParams) {
        this.router.navigate(["Records", this.backUrlParams]);
      } else {
        this.router.navigate(["Records"]);
      }
    }
}
