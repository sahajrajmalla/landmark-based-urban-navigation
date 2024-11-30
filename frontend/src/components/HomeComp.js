import React, { useState } from 'react'
import Hashes from "../assets/data.json"
import dynamic from "next/dynamic"

const Map = dynamic(() => import("../components/MapComponent.js"), { ssr:false })
 


// const dropItems = [
//   {
//     title: 'A-005-LTR-CD',
//     description: [
//       {
//         symbol: 'A',
//         meaning: 'America'
//       },
//       {
//         symbol: 'LTR',
//         meaning: 'Lorem'
//       },
//       {
//         symbol: '005',
//         meaning: '5 Lorem'
//       },


//     ]
//   },
//   {
//     title: 'A-005-LTR-CD',
//     description: [
//       {
//         symbol: 'A',
//         meaning: 'America'
//       },
//       {
//         symbol: 'LTR',
//         meaning: 'Lorem'
//       },
//       {
//         symbol: '005',
//         meaning: '5 Lorem'
//       },


//     ]
//   },
//   {
//     title: 'A-005-LTR-CD',
//     description: [
//       {
//         symbol: 'A',
//         meaning: 'America'
//       },
//       {
//         symbol: 'LTR',
//         meaning: 'Lorem'
//       },
//       {
//         symbol: '005',
//         meaning: '5 Lorem'
//       },


//     ]
//   },
//   {
//     title: 'A-005-LTR-CD',
//     description: [
//       {
//         symbol: 'A',
//         meaning: 'America'
//       },
//       {
//         symbol: 'LTR',
//         meaning: 'Lorem'
//       },
//       {
//         symbol: '005',
//         meaning: '5 Lorem'
//       },


//     ]
//   },
//   {
//     title: 'A-005-LTR-CD',
//     description: [
//       {
//         symbol: 'A',
//         meaning: 'America'
//       },
//       {
//         symbol: 'LTR',
//         meaning: 'Lorem'
//       },
//       {
//         symbol: '005',
//         meaning: '5 Lorem'
//       },


//     ]
//   },
//   {
//     title: 'A-005-LTR-CD',
//     description: [
//       {
//         symbol: 'A',
//         meaning: 'America'
//       },
//       {
//         symbol: 'LTR',
//         meaning: 'Lorem'
//       },
//       {
//         symbol: '005',
//         meaning: '5 Lorem'
//       },


//     ]
//   },
//   {
//     title: 'A-005-LTR-CD',
//     description: [
//       {
//         symbol: 'A',
//         meaning: 'America'
//       },
//       {
//         symbol: 'LTR',
//         meaning: 'Lorem'
//       },
//       {
//         symbol: '005',
//         meaning: '5 Lorem'
//       },


//     ]
//   },
//   {
//     title: 'A-005-LTR-CD',
//     description: [
//       {
//         symbol: 'A',
//         meaning: 'America'
//       },
//       {
//         symbol: 'LTR',
//         meaning: 'Lorem'
//       },
//       {
//         symbol: '005',
//         meaning: '5 Lorem'
//       },


//     ]
//   },



// ]

const itemsPerPage = 900;

let buildings = [];

const customMarkers = [
  { info: 'K-35-RTY-MD', lat: 51.506, lng: -0.08 },
  // Add more custom markers
];


function HomeCompo(props) {
  const [activeMarker, setActiveMarker] = useState(null)
  const [currentPage, setCurrentPage] = useState(1);

  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;

  let itemsToShow = Hashes.slice(startIndex, endIndex);

  if (props.isSearch && props.searchData){
    itemsToShow = itemsToShow.filter(item=>item.name && item.name.toLowerCase().includes(props.searchData.toLowerCase()))
  }

  buildings = itemsToShow? itemsToShow : []

  const [dropdown, setDropdown] = useState(null)


  const dropdownChangeHandler = (index) => {


    if (index === dropdown && dropdown != null) {
      setDropdown(null)
    } else {
      setDropdown(index)
    }
  }
  
 

  return (
    <div className='pl-12 w-full flex h-max'>
      <div className='w-1/2 mt-10 space-y-8 h-full flex flex-col'>
        <div className='flex gap-4 items-center'>
          <svg xmlns="http://www.w3.org/2000/svg" width="8" height="14" viewBox="0 0 8 14" fill="none">
            <path d="M6 2L2 7L6 12" stroke="black" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <p className='text-xl font-bold'>Home</p>
        </div>

        <div className='flex space-y-2 pr-12 text-md flex-col'>
          <p>Found <span className='text-primary font-semibold'>{props.isSearch && props.searchData? itemsToShow.length : '22000+' }</span> Hashes</p>
          <hr className='border' />

          <div className='w-full flex flex-col gap-4 pr-12 h-[66vh] container-snap overflow-scroll'>


            {itemsToShow.map((i, index) => {
              let i_cut = i.hashes.split('|')
              let i_name = i_cut[0]  + i_cut[i_cut.length-1]
              let remainingCharacters = i_cut.slice(1);
              // console.log(remainingCharacters)
              return (
                <div key={i_name+index} className="rounded-xl w-full bg-gray-50 border  px-6 py-3">
                  <button onClick={() => dropdownChangeHandler(index)} className="flex overflow-scroll container-snap w-full items-center justify-between">
                    <h1 className="text-gray-700 text-sm font-semibold tracking-wide">
                      {i_name}
                    </h1>

                    <span className="flex h-8 w-8 items-center justify-center rounded-full  text-dark">
                      <svg
                        className="fill-gray-700 h-4 w-4"
                        viewBox="0 0 30 30"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path d="M7.5 9L15 16.5L22.5 9L25.5 10.5L15 21L4.5 10.5L7.5 9Z" />
                      </svg>
                    </span>
                  </button>
                  {dropdown == index && <div className='mt-2'>
                    <p className='text-sm font-semibold text-gray-400'>Denotion</p>
                    <div className='flex mt-2 justify-between'>

                      {remainingCharacters.map(item => <p key={item.hashes} className='text-[12px]'>{item}</p>)}

                    </div>
                    <div className='w-full mt-2'>
                    <p className='text-sm font-semibold text-gray-400  container-snap'>Hash</p>
                    <div className='flex mt-2 justify-between w-full overflow-scroll container-snap'>

                      {i.hashes}

                    </div>
                    </div>

                  </div>}

                </div>
              )
            })}


          </div>
        </div>


        <div>

        </div>
      </div>
      <div className=' w-1/2 h-[89vh] bg-gray-500 gap-4 font-semibold flex'>
        <Map buildings={buildings} customMarkers={customMarkers} activeMarker = {dropdown} />
      </div>
    </div>
  )
}

export default HomeCompo