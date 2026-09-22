import { View } from 'react-native';import { ActivityIndicator,Button,Text } from 'react-native-paper';
export function Loading(){return <View style={{padding:32,alignItems:'center'}}><ActivityIndicator accessibilityLabel="Yükleniyor"/><Text>Yükleniyor…</Text></View>}
export function Empty({message='Henüz kayıt yok.'}:{message?:string}){return <View style={{padding:32,alignItems:'center'}}><Text variant="titleMedium">{message}</Text></View>}
export function ErrorState({retry}:{retry:()=>void}){return <View style={{padding:32}}><Text>Veriler alınamadı. Bağlantınızı kontrol edin.</Text><Button onPress={retry}>Yeniden dene</Button></View>}
