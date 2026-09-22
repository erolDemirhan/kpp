import AsyncStorage from '@react-native-async-storage/async-storage';
import { QueryClient } from '@tanstack/react-query';
export const queryClient=new QueryClient({defaultOptions:{queries:{staleTime:60_000,retry:2}}});
export async function persistSnapshot(key:string,value:unknown){await AsyncStorage.setItem(`cache:${key}`,JSON.stringify({value,savedAt:new Date().toISOString()}));}
export async function readSnapshot<T>(key:string):Promise<{value:T;savedAt:string}|null>{const raw=await AsyncStorage.getItem(`cache:${key}`);return raw?JSON.parse(raw):null;}
