use rodio::cpal::traits::{DeviceTrait, HostTrait};
use rodio::*;
use std::fs::File;
use std::io::BufReader;

#[allow(dead_code)]
fn list_host_devices() {
    let host = cpal::default_host();
    let devices = host.output_devices().unwrap();
    for device in devices {
        let dev: rodio::Device = device.into();
        let dev_name: String = dev.name().unwrap();
        println!(" # Device : {}", dev_name);
    }
}

fn get_output_stream(device_name: &str) -> (OutputStream, OutputStreamHandle) {
    let host = cpal::default_host();
    let devices = host.output_devices().unwrap();
    let (mut _stream, mut stream_handle) = OutputStream::try_default().unwrap();
    for device in devices {
        let dev: rodio::Device = device.into();
        let dev_name: String = dev.name().unwrap();
        if dev_name == device_name {
            println!("Device found: {}", dev_name);
            (_stream, stream_handle) = OutputStream::try_from_device(&dev).unwrap();
        }
    }
    return (_stream, stream_handle);
}

fn main() {
    // list_host_devices();
    let (_stream, stream_handle) = get_output_stream("CABLE Input (VB-Audio Virtual Cable)");
    let sink = Sink::try_new(&stream_handle).unwrap();
    let file = File::open("output.wav").unwrap();
    let source = rodio::Decoder::new(BufReader::new(file)).unwrap();
    sink.append(source);
    sink.sleep_until_end();
    // Delete the sink to stop the playback.
    drop(sink);
}