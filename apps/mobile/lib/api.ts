import AsyncStorage from '@react-native-async-storage/async-storage';
const BASE=process.env.EXPO_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
export type Instrument={id:string;symbol:string;name:string;type:'fx'|'index'|'equity'|'fund';currency:string};
export type Quote={instrument_id:string;provider:string;quote_type:string;value:string;currency:string;unit:string;as_of:string;received_at:string;delay_seconds:number;status:string;valuation_date?:string};
export async function api<T>(path:string,options:RequestInit={}):Promise<T>{
  const token=await AsyncStorage.getItem('firebaseToken');
  const response=await fetch(`${BASE}${path}`,{...options,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{'X-Demo-User':'demo-user'}),...options.headers}});
  if(!response.ok)throw new Error((await response.json().catch(()=>null))?.detail ?? 'Sunucuya ulaşılamadı');
  if(response.status===204)return undefined as T;
  return response.json();
}
export const formatValue=(value:string|number,currency:string)=>new Intl.NumberFormat('tr-TR',{style:currency==='POINT'?'decimal':'currency',currency:currency==='POINT'?'TRY':currency,maximumFractionDigits:currency==='POINT'?2:6}).format(Number(value))+(currency==='POINT'?' puan':'');
