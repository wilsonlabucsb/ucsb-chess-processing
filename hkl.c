#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <unistd.h>
#include <sys/time.h>
#include <stdarg.h>
//#include <iostream.h>

#include <omp.h>





double  dotf         (double* a, double* b, int size);//dot product
void   cross3f      (double* a, double* b, double* v);//3 element vector cross product
void   trans3f      (double A[3][3], double M[3][3]);//transpose a 3x3 matrix
void   MatrixMultf  (double A[3][3], double B[3][3], double C[3][3]);//multiplies 2 matrices
void   MatrixMultPf  (double A[3][3], double B[3][3], double C[3][3]);//multiplies 2 matrices
void   MVMult3f     (double* vin, double B[3][3], double* vout);
double  determ3f     (double A[3][3]);//determinant of 3x3 matrix
void   inverse3f    (double A[3][3], double invA[3][3]);//inverse of a 3x3 matrix
double getclock     ();//timing function


void calchkl(double *P, double *A,double eta,double mu,double chi,double phi,double WL,double *U,double *HR, double *KR,double *LR,int N);

void hist(double *Hbin,double *Kbin,double *Lbin,double *HR,double *KR,double *LR,float *counts,float *vol,float *norm,float *errors,int N,int hn,int kn,int ln,float mon);

void histarb(double *Q1bin,double *Q2bin,float *phat,double *HR,double *KR,double *LR,float *vec1,float *vec2,float prangemin,float prangemax,float *counts,float *vol,float *norm,int N,int lenQ1,int lenQ2,float mon);


//arbitrary planar histogram for free slicing
void histarb(double *Q1bin,double *Q2bin,float *phat,double *HR,double *KR,double *LR,float *vec1,float *vec2,float prangemin,float prangemax,float *counts,float *vol,float *norm,int N,int lenQ1,int lenQ2,float mon)
{

	double v1conv[N],v2conv[N],pconv[N];
	int i,n,Q1index,Q2index;

//	printf("pmin is %4.2f, pmax is %4.2f",prangemin,prangemax);

	#pragma omp parallel for private(i,n,Q1index,Q2index)
	for (n=0;n<N;n++)
	{
		//add if counts[n]>0 condition to deal with blank bars
		if (counts[n]>=0.0)
		{
			Q1index=0;
			Q2index=0;
			pconv[n]=(HR[n]*phat[0])+(KR[n]*phat[1])+(LR[n]*phat[2]);
//			printf("\n Pconv[n] = %4.4f",pconv[n]);
			if (pconv[n]>prangemin && pconv[n]<prangemax)
			{
//				printf("pconv ok");
				v1conv[n]=(HR[n]*vec1[0])+(KR[n]*vec1[1])+(LR[n]*vec1[2]);
				if (v1conv[n]>Q1bin[0] && v1conv[n]<Q1bin[lenQ1-1])
				{ 
//					printf("v1conv ok");
					v2conv[n]=(HR[n]*vec2[0])+(KR[n]*vec2[1])+(LR[n]*vec2[2]);
					if (v2conv[n]>Q2bin[0] && v2conv[n]<Q2bin[lenQ2-1])
					{
//						printf("v2conv ok");
						for (i=1;i<lenQ1;i++)
						{
							if (Q1bin[i]>v1conv[n])
							{
								Q1index=i-1;
								//printf("Found one Q1");
								break;
							}
						}
						for (i=1;i<lenQ2;i++)
						{
							if (Q2bin[i]>v2conv[n])
							{
								Q2index=i-1;
								//printf("Found one Q2");
								break;
							}
						}
						#pragma omp atomic
						//vol[(Q1index*lenQ1)+Q2index]+=counts[n]/mon;
						vol[(Q1index*lenQ2)+Q2index]+=counts[n]/mon;
						#pragma omp atomic
						//norm[(Q1index*lenQ1)+Q2index]+=1.0;
						norm[(Q1index*lenQ2)+Q2index]+=1.0;
					}
				}
			}
		}	
	}
}


////////////////////////////////////////////////////////////////////////////////////////////




//need to use openmp on the hist routine

void hist(double *Hbin,double *Kbin,double *Lbin,double *HR,double *KR,double *LR,float *counts,float *vol,float *norm,float *errors,int N,int hn,int kn,int ln,float mon)
{
	int i,j,k,hin,kin,lin;
	int n,flag,index,flag2=0;


	//printf("\n %i %i %i %i\n",N,hn,kn,ln);
	//loop over list of hkl's that need to be histogrammed
	#pragma omp parallel for private(n,i,flag,flag2,hin,kin,lin,index)
	for (n=0;n<N;n++)
	{
		//add if counts[n]>0 condition to deal with blank bars
		if (counts[n]>=0.0)
		{
			hin=0;
			kin=0;
			lin=0;
			flag=0;
			flag2=0;
			//determin the h index value for the data to be stored
			//what happens with this loop... i think open mp is breaking these up as well?
			if (HR[n]>Hbin[0] && HR[n]<Hbin[hn-1])
			{
				flag=0;
				for (i=1;i<hn;i++)
				{
					if (flag==0 && Hbin[i]>HR[n])
					{
						flag=1;
						hin=i-1;
						break;
					}
				}
			}
			else
			{
			   flag2=1;
			}
			
			//determin the k index value 
			if (KR[n]>Kbin[0] && KR[n]<Kbin[kn-1] && flag2==0)
			{
				flag=0;
				for (i=1;i<kn;i++)
				{
					if (flag==0 && Kbin[i]>KR[n])
					{
						flag=1;
						kin=i-1;
						break;
					}
				}
			}
			else
			{
			   flag2=1;
			}
			flag=0;
			//determin the l index 
			if (LR[n]>Lbin[0] && LR[n]<Lbin[ln-1] && flag2==0)
			{
				flag=0;
				for (i=1;i<ln;i++)
				{
					if (flag==0 && Lbin[i]>LR[n])
					{
						flag=1;
						lin=i-1;
						break;
					}
				}
			}
			else
			{
			   flag2=1;
			}
			
			//index = linearized [i][j][k]
	
			if(flag2==0)
			{
				
				index=hin*kn*ln+ln*kin+lin;
				//printf("%d %d %d %d\n",index,hn,kn,ln);
				//need to sync threads here
				#pragma omp atomic
				vol[index]+=counts[n]/mon;
				#pragma omp atomic
				errors[index]+=0;
				#pragma omp atomic
				norm[index]+=1.0;
			}
		
		}
	}
}



//function to use in python
//this one is not using openmp or precalc
//right now mu and  aren't used and should be zero
void calchkl(double *P, double *A,double eta,double mu,double chi,double phi,double WL,double *U,double *HR, double *KR,double *LR,int N)
{

//define all the matricies... don't like using malloc...
	int i;
	double Umatrix[3][3];
	
	double Uinv[3][3];
	
	double OMEGA[3][3];
	double PHI[3][3];
	double CHI[3][3];
	double ETA[3][3];
	double MU[3][3];
	double OMEGAINV[3][3];
	double PHIINV[3][3];
	double CHIINV[3][3],M[3][3];
	double ETAINV[3][3];
	double MUINV[3][3];
	double omega;
	double q[3],hklvector[3];
	double ki;
	double T1[3][3],T2[3][3], T3[3][3], T4[3][3];

	
	Umatrix[0][0]=U[0];
	Umatrix[0][1]=U[1];
	Umatrix[0][2]=U[2];
	Umatrix[1][0]=U[3];
	Umatrix[1][1]=U[4];
	Umatrix[1][2]=U[5];
	Umatrix[2][0]=U[6];
	Umatrix[2][1]=U[7];
	Umatrix[2][2]=U[8];

	

    //printf("Got mu");
	

	//compute phi and chi and eta (and mu) matricies and inverses

	PHI[0][0]=cos(phi);
	PHI[0][1]=-1.0*sin(phi);
	PHI[0][2]=0.0;
	PHI[1][0]=sin(phi);
	PHI[1][1]=cos(phi);
	PHI[1][2]=0.0;
	PHI[2][0]=0.0;
	PHI[2][1]=0.0;
	PHI[2][2]=1.0;

	CHI[0][0]=cos(chi);
	CHI[0][1]=0.0;
	CHI[0][2]=-1.0*sin(chi);
	CHI[1][0]=0.0;
	CHI[1][1]=1.0;
	CHI[1][2]=0.0;
	CHI[2][0]=sin(chi);
	CHI[2][1]=0.0;
	CHI[2][2]=cos(chi);

	ETA[0][0]=cos(eta);
	ETA[0][1]=-1.0*sin(eta);
	ETA[0][2]=0.0;
	ETA[1][0]=sin(eta);
	ETA[1][1]=cos(eta);
	ETA[1][2]=0.0;
	ETA[2][0]=0.0;
	ETA[2][1]=0.0;
	ETA[2][2]=1.0;

	MU[0][0]=1.0;
	MU[0][1]=0.0;
	MU[0][2]=0.0;
	MU[1][0]=0.0;
	MU[1][1]=cos(mu);
	MU[1][2]=-1.0*sin(mu);
	MU[2][0]=0.0;
	MU[2][1]=sin(mu);
	MU[2][2]=cos(mu);

	//compute inverse matricies
	inverse3f(Umatrix,Uinv);
	
	inverse3f(CHI,CHIINV);
	inverse3f(PHI,PHIINV);
	inverse3f(ETA,ETAINV);
	inverse3f(MU,MUINV);

	ki=1.0/WL;
	

	//MatrixMultf(Uinv,Binv,T1);
    	//MatrixMultf(PHIINV,T1,T2);
       // MatrixMultf(CHIINV,T2,T1);
	MatrixMultf(MUINV,ETAINV,T4);
	MatrixMultf(T4,CHIINV,T3);
	MatrixMultf(T3,PHIINV,T2);
//changes made to use spec's or matrix

//	MatrixMultf(T2,Uinv,T1);
//	MatrixMultf(T1,Binv,T2);

	MatrixMultf(T2,Uinv,T1);
//	T2=T1;
	//printf("\n%lf %lf %lf\n%lf %lf %lf\n %lf %lf %lf\n",T1[0][0],T1[0][1],T1[0][2],T1[1][0],T1[1][1],T1[1][2],T1[2][0],T1[2][1],T1[2][2]);

//#pragma omp parallel for private(T1,T2,hklvector,i,M,OMEGAINV,OMEGA,q,P,A) 

	#pragma omp parallel for private(i,q,omega,OMEGA,OMEGAINV,T2,M,hklvector)
	for(i=0;i<N;i++)
	{
		//compute omega 
		
		q[0]=ki*sqrt(1.0-2*cos(A[i])*cos(P[i])+cos(A[i])*cos(A[i]));
		q[1]=0.0; //probably get this out of the loop... compiler should take care of that though
		q[2]=sin(A[i])*ki;
		if (P[i]<0.0)
		{
			q[0]=q[0]*-1.0;
					
		}
		else
		{
			
		}
		omega=-1.0*atan((1.0-cos(A[i])*cos(P[i]))/(cos(A[i])*sin(P[i])));
		OMEGA[0][0]=cos(omega);
      		OMEGA[0][1]=-sin(omega);
	        OMEGA[1][0]=sin(omega);
      		OMEGA[1][1]=cos(omega);
		OMEGA[0][2]=0.0;//these values are constant can probably take them out of the loop.... 
		OMEGA[1][2]=0.0;
		OMEGA[2][0]=0.0;
		OMEGA[2][1]=0.0;
		OMEGA[2][2]=1.0;
		//compute omega inverse
		inverse3f(OMEGA,OMEGAINV);
		//calculate q vector
		
		
		//printf("%lf %lf %lf\n",q[0],q[1],q[2]);
		MatrixMultf(OMEGAINV,T1,T2);
		
		//printf("\n%lf %lf %lf\n%lf %lf %lf\n %lf %lf %lf\n",T1[0][0],T1[0][1],T1[0][2],T1[1][0],T1[1][1],T1[1][2],T1[2][0],T1[2][1],T1[2][2]);

		trans3f(T2,M);
		hklvector[0]=dotf(q,M[0],3);   
		hklvector[1]=dotf(q,M[1],3);   
		hklvector[2]=dotf(q,M[2],3);
		//printf("%lf %lf %lf\n\n",hklvector[0],hklvector[1],hklvector[2]);
		HR[i]=hklvector[0];
		KR[i]=hklvector[1];
		LR[i]=hklvector[2];
		
	}
	
}








//dot product of 2 vectors
double dotf(double* a, double* b, int size){
      int i;
      double sum=0.0;
      for(i=0;i<size;i++)sum+= a[i]*b[i];
      return sum;
}



// Cross product of 3 element vectors
void cross3f(double* a, double* b, double* v){
      v[0]=a[1]*b[2]-a[2]*b[1];
      v[1]=a[2]*b[0]-a[0]*b[2];
      v[2]=a[0]*b[1]-a[1]*b[0];
}



//transpose 3x3 matrix
void trans3f(double A[3][3], double M[3][3]){
     int i,j;
     for(i=0;i<3;i++){
	for(j=0;j<3;j++){
	     M[i][j]=A[j][i];
	}
     }
}



//matrix multiplication, with A leading imax and B leading jmax 
//so that C is imax by jmax
void MatrixMultPf(double A[3][3], double B[3][3], double C[3][3]){

     int i,j;
     double M[3][3];
     
     trans3f(B,M);
     
     for(i=0;i<3;i++){
	for(j=0;j<3;j++){
	   C[i][j]=dotf(A[i],M[j],3);
	}
     }
     
}



//matrix multiplication, with A leading imax and B leading jmax 
//so that C is imax by jmax
void MatrixMultf(double A[3][3], double B[3][3], double C[3][3]){

     int i,j;
     double M[3][3];
     
     for(i=0;i<3;i++){
	for(j=0;j<3;j++){
	     M[i][j]=B[j][i];
	}
     }
     
     for(i=0;i<3;i++){
	for(j=0;j<3;j++){
	   C[i][j]=dotf(A[i],M[j],3);
	}
     }
     
     
}




void MVMult3f(double* vin, double B[3][3], double* vout){
     int i;
     double M[3][3];
     
     trans3f(B,M);
     
     for(i=0;i<3;i++)vout[i]=dotf(vin,M[i],3);   
      
}



//calculate the determinant of a 3x3 matrix
double determ3f(double A[3][3]){
  double retval=0.0;
  retval+=A[0][0]*A[1][1]*A[2][2];
  retval+=A[0][1]*A[1][2]*A[2][0];
  retval+=A[0][2]*A[1][0]*A[2][1];
  retval-=A[2][0]*A[1][1]*A[0][2];
  retval-=A[2][1]*A[1][2]*A[0][0];
  retval-=A[2][2]*A[1][0]*A[0][1];
  return retval;
}






//calculate inverse matrix of a 3x3 matrix
void inverse3f(double A[3][3], double invA[3][3]){
     double detA=determ3f(A);
     // printf("detA: %f\n",detA);
     double M[3][3];
 

     trans3f(A,M);

     double r[3][3];
     cross3f(M[1],M[2],r[0]);
     cross3f(M[2],M[0],r[1]);
     cross3f(M[0],M[1],r[2]);
     
     int i,j;
     for(i=0;i<3;i++){
	for(j=0;j<3;j++){
	   invA[i][j]=r[i][j]/detA;
	}
     }

     
}




double getclock(){
      struct timezone tzp;
      struct timeval tp;
      gettimeofday (&tp, &tzp);
      return (tp.tv_sec + tp.tv_usec*1.0e-6);
}



