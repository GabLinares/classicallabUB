using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ParticleCollider : MonoBehaviour
{
    // Start is called before the first frame update
    public GameObject camera;
    public Computation script;
    
    void Start()
    {
        camera = GameObject.FindWithTag("MainCamera");
        script = camera.GetComponent<Computation>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    void OnTriggerEnter2D(Collider2D col)
    {
        int npart;
        npart = System.Convert.ToInt32(col.name);
        if(this.tag == "side")
        {
            script.v0[npart, 0] = -1 * script.v0[npart, 0];
        }
        if (this.tag == "topdown")
        {
            script.v0[npart, 1] = -1 * script.v0[npart, 1];
        }



    }
}
